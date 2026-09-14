"""TAGO transport, with bounded pagination and secret-free diagnostics."""
import logging
import os
import time
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
BASE = 'https://apis.data.go.kr/1613000/TrainInfo'
env_path = ROOT / '.env'
env_encoding = 'utf-16' if env_path.is_file() and env_path.read_bytes()[:2] in (b'\xff\xfe', b'\xfe\xff') else 'utf-8-sig'
load_dotenv(env_path, encoding=env_encoding)
AUTH_CODES = {'20', '21', '22', '30', '31', '32', '33'}


class APIError(Exception):
    def __init__(self, kind, message, http_status=None, api_code=None):
        super().__init__(message)
        self.info = dict(kind=kind, message=message, http_status=http_status, api_code=api_code)


def get(operation, **params):
    key = unquote(os.getenv('SERVICE_KEY', ''))
    if not key or key == 'YOUR_SERVICE_KEY':
        raise APIError('AUTH_ERROR', 'SERVICE_KEY 설정을 확인하세요.')
    rows = []
    for page in range(1, 101):
        started = time.monotonic()
        try:
            response = requests.get(f'{BASE}/{operation}', params={**params, 'serviceKey': key,
                                    '_type': 'json', 'pageNo': page, 'numOfRows': 100}, timeout=15)
        except requests.RequestException:
            raise APIError('NETWORK_ERROR', '외부 API 연결에 실패했습니다.') from None
        logging.getLogger('app').info('operation=%s http=%s elapsed=%.3f', operation,
                                     response.status_code, time.monotonic() - started)
        if response.status_code in (401, 403):
            raise APIError('AUTH_ERROR', 'API 인증이 거부되었습니다.', response.status_code)
        if not response.ok:
            try:
                gateway = response.json().get('OpenAPI_ServiceResponse', {}).get('cmmMsgHeader', {})
                gateway_code = str(gateway.get('returnReasonCode', ''))
            except (ValueError, AttributeError, TypeError):
                gateway_code = ''
            if gateway_code == '12':
                raise APIError('API_ERROR', '공공데이터 서버가 해당 API 서비스를 찾지 못했습니다. 서비스 주소와 제공 상태를 확인해야 합니다.', response.status_code, '12')
            if gateway_code in AUTH_CODES:
                raise APIError('AUTH_ERROR', 'API 인증 설정을 확인하세요.', response.status_code, gateway_code)
            raise APIError('HTTP_ERROR', '외부 API HTTP 오류입니다.', response.status_code)
        try:
            data = response.json()['response']
            code = str(data['header']['resultCode'])
        except (ValueError, KeyError, TypeError):
            try:
                code = ElementTree.fromstring(response.text).findtext('.//returnReasonCode')
            except ElementTree.ParseError:
                code = None
            if code in AUTH_CODES:
                raise APIError('AUTH_ERROR', 'API 인증 설정을 확인하세요.', response.status_code, code) from None
            raise APIError('PARSE_ERROR', 'JSON 응답 구조를 확인할 수 없습니다.', response.status_code) from None
        # Never forward upstream text: even errors can echo the credential.
        safe_code = code if code.isdigit() and len(code) <= 3 else None
        logging.getLogger('app').info('operation=%s api_code=%s', operation, safe_code)
        if code not in ('00', '0'):
            if code == '03':
                return []
            raise APIError('AUTH_ERROR' if code in AUTH_CODES else 'API_ERROR',
                           '공공데이터 API가 오류를 반환했습니다.', response.status_code, safe_code)
        try:
            body = data['body']
            items = body.get('items') or {}
            batch = items.get('item', [])
            if isinstance(batch, dict):
                batch = [batch]
            if not isinstance(batch, list) or any(not isinstance(row, dict) for row in batch):
                raise ValueError()
            rows.extend(batch)
            total = int(body.get('totalCount', len(rows)))
        except (ValueError, TypeError, AttributeError, KeyError):
            raise APIError('PARSE_ERROR', '목록 응답 형식이 올바르지 않습니다.') from None
        if len(rows) >= total:
            return rows
        if not batch:
            raise APIError('PARSE_ERROR', '페이지 목록이 누락되었습니다.')
    raise APIError('API_ERROR', '최대 페이지 수를 초과했습니다.')
