"""Run once: inspect -> classify -> recover once -> verify -> report."""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from api_client import APIError, ROOT
from app import setup_log, validate
from health_check import api_probes, base_url, check, dns, local_health, port_open, prerequisites

GOOD = {'OK', 'NO_DATA'}
RETRYABLE = {'NETWORK_ERROR', 'HTTP_ERROR', 'API_ERROR', 'PARSE_ERROR'}


def start_service():
    # Only launch our own app on its fixed port; never kill an unknown process.
    if port_open():
        return False
    kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if sys.platform == 'win32' else {'start_new_session': True}
    subprocess.Popen([sys.executable, str(ROOT / 'app.py')], cwd=ROOT,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    for _ in range(20):
        time.sleep(.25)
        if check('HTTP', local_health)['status'] == 'OK':
            return True
    return False


def screen_probe(path):
    try:
        response = requests.get('http://127.0.0.1:5000' + path, timeout=45)
        if response.status_code != 200:
            raise APIError('HTTP_ERROR', '화면 요청 검증 실패', response.status_code)
        if path != '/':
            data = response.json()
            if not isinstance(data.get('items'), list):
                raise ValueError()
        return 'OK'
    except requests.RequestException:
        raise APIError('NETWORK_ERROR', '로컬 화면 요청 실패') from None
    except (ValueError, AttributeError):
        raise APIError('PARSE_ERROR', '로컬 JSON 응답 오류') from None


def run(args):
    logger = setup_log('agent')
    report = dict(status='ERROR', prerequisites=prerequisites(), checks=[], recovery=[], verification=[])
    try:
        params, _, _ = validate(vars(args))
        if not args.city_code.isdigit():
            raise APIError('INVALID_INPUT', '도시코드는 숫자여야 합니다.')
    except APIError as error:
        report['input_error'] = error.info
        return report
    pre = report['prerequisites']
    if pre['missing_files'] or pre['missing_packages'] or not pre['env_exists']:
        return report
    service = check('FLASK_PROCESS_HTTP', local_health)
    report['checks'].append(service)
    report['checks'].append(dict(name='PORT', status='OK' if port_open() else 'PORT_CLOSED'))
    recovered = False
    if service['status'] != 'OK' and args.recover:
        occupied = port_open()
        started = start_service()
        report['recovery'].append(dict(target='FLASK', attempted=not occupied,
                                       result='STARTED' if started else 'FAILED_OR_PORT_OCCUPIED'))
        recovered = started
        service = check('FLASK_PROCESS_HTTP', local_health)
        report['verification'].extend([service, dict(name='PORT', status='OK' if port_open() else 'PORT_CLOSED')])
    final = [service]
    network = check('DNS', dns)
    if network['status'] != 'OK' and args.recover:
        report['checks'].append(network)
        network = check('DNS', dns)
        report['recovery'].append(dict(target='DNS', result=network['status']))
        recovered |= network['status'] == 'OK'
    report['checks'].append(network)
    final.append(network)
    if network['status'] == 'OK':
        report['checks'].append(check('BASE_URL', base_url))
        for name, action in api_probes(args.city_code, params).items():
            probe = check(name, action)
            # Store only counts, never API rows or upstream text in operational logs.
            if isinstance(probe.get('detail'), list):
                probe['detail'] = {'count': len(probe['detail'])}
            report['checks'].append(probe)
            if probe['status'] in RETRYABLE and args.recover:
                probe = check(name, action)
                if isinstance(probe.get('detail'), list):
                    probe['detail'] = {'count': len(probe['detail'])}
                report['recovery'].append(dict(target=name, result=probe['status']))
                report['verification'].append(probe)
                recovered |= probe['status'] in GOOD
            if probe['status'] not in GOOD:
                probe['classification'] = name + '_ERROR'
            final.append(probe)
    else:
        report['checks'].extend(dict(name=name, status='SKIPPED', message='DNS 실패로 원인 판정 보류')
                                for name in api_probes(args.city_code, params))
    if recovered and service['status'] == 'OK':
        from urllib.parse import urlencode
        verification = [check('FLASK_PROCESS_HTTP', local_health),
                        dict(name='PORT', status='OK' if port_open() else 'PORT_CLOSED')]
        verification.extend(check('SCREEN ' + path.split('?')[0], lambda path=path: screen_probe(path))
                            for path in ['/', '/cities', '/stations?' + urlencode({'city_code': args.city_code}),
                                         '/train-types', '/search?' + urlencode({key: value for key, value in vars(args).items()
                                                                                if key not in ('recover', 'city_code') and value is not None})])
        report['verification'].extend(verification)
        final.extend(verification)
    failed = any(p['status'] not in GOOD for p in final)
    warning = any(p['status'] == 'NO_DATA' or p.get('elapsed', 0) > 5 for p in final)
    report['status'] = 'ERROR' if failed else 'RECOVERED' if recovered else 'WARNING' if warning else 'OK'
    report['logs'] = {name: {'exists': (ROOT / 'logs' / name).is_file(),
                             'bytes': (ROOT / 'logs' / name).stat().st_size if (ROOT / 'logs' / name).is_file() else 0}
                      for name in ('app.log', 'agent.log')}
    logger.info('%s', json.dumps(report, ensure_ascii=False))
    return report


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='TAGO 서비스 및 4개 API 운영 점검')
    parser.add_argument('--recover', action='store_true', help='서비스 시작 및 실패 API 재시도를 각각 최대 1회 허용')
    parser.add_argument('--city-code', default='11')
    parser.add_argument('--departure', default='NAT010000')
    parser.add_argument('--arrival', default='NAT014445')
    parser.add_argument('--date', default=datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y-%m-%d'))
    parser.add_argument('--start-time', default='00:00')
    parser.add_argument('--end-time', default='23:59')
    parser.add_argument('--train-type', default='')
    result = run(parser.parse_args())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(1 if result['status'] == 'ERROR' else 0)
