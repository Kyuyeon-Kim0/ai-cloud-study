"""Independent probes; this module never changes system configuration."""
import importlib.util
import socket
import sys
import time

import requests
from api_client import APIError, BASE, ROOT, get


def check(name, action):
    start = time.monotonic()
    try:
        detail = action()
        return dict(name=name, status='NO_DATA' if detail == [] else 'OK',
                    elapsed=round(time.monotonic() - start, 3), detail=detail)
    except APIError as error:
        return dict(name=name, status=error.info['kind'], error=error.info,
                    elapsed=round(time.monotonic() - start, 3))
    except Exception:
        return dict(name=name, status='UNKNOWN_ERROR', message='점검 실행에 실패했습니다.')


def port_open():
    try:
        with socket.create_connection(('127.0.0.1', 5000), timeout=2):
            return True
    except OSError:
        return False


def local_health():
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=3)
        data = response.json()
        if response.status_code != 200 or data.get('service') != 'tago-train' or not isinstance(data.get('pid'), int):
            raise ValueError()
        return data
    except (requests.RequestException, ValueError, AttributeError):
        raise APIError('SERVICE_DOWN', 'TAGO 서비스 응답을 확인하지 못했습니다.') from None


def dns():
    try:
        socket.getaddrinfo('apis.data.go.kr', 443)
        return 'DNS_OK'
    except OSError:
        raise APIError('NETWORK_ERROR', '공공데이터 DNS 조회에 실패했습니다.') from None


def base_url():
    try:
        response = requests.get(BASE, timeout=10)
        # A base URL need not be an API resource; 404 still proves HTTP reachability.
        return dict(http_status=response.status_code, reachable=True)
    except requests.RequestException:
        raise APIError('NETWORK_ERROR', '공공데이터 서버에 연결할 수 없습니다.') from None


def prerequisites():
    files = ['app.py', 'api_client.py', 'health_check.py', 'agent.py', 'templates/index.html', 'static/app.js', 'static/style.css']
    return dict(python=sys.version.split()[0], env_exists=(ROOT / '.env').is_file(),
                missing_files=[name for name in files if not (ROOT / name).is_file()],
                missing_packages=[name for name in ['flask', 'requests', 'dotenv'] if importlib.util.find_spec(name) is None])


def api_probes(city_code, params):
    return {
        'CITY_API': lambda: get('GetCtyCodeList'),
        'STATION_API': lambda: get('GetCtyAcctoTrainSttnList', cityCode=city_code),
        'VEHICLE_API': lambda: get('GetVhcleKndList'),
        'TIMETABLE_API': lambda: get('GetStrtpntAlocFndTrainInfo', **params),
    }
