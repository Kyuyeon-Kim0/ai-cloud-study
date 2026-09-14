import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask, jsonify, render_template, request
from api_client import ROOT, APIError, get

app = Flask(__name__)


def setup_log(name):
    (ROOT / 'logs').mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RotatingFileHandler(ROOT / 'logs' / f'{name}.log', maxBytes=1_000_000, backupCount=3, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


setup_log('app')


def validate(values):
    departure, arrival = values.get('departure', '').strip(), values.get('arrival', '').strip()
    try:
        date = datetime.strptime(values.get('date', ''), '%Y-%m-%d').date()
        start = datetime.strptime(values.get('start_time', '00:00'), '%H:%M').time()
        end = datetime.strptime(values.get('end_time', '23:59'), '%H:%M').time()
        if not departure or not arrival or departure == arrival or start > end or date < datetime.now(ZoneInfo('Asia/Seoul')).date():
            raise ValueError()
    except (ValueError, TypeError):
        raise APIError('INVALID_INPUT', '서로 다른 출발·도착역, 오늘 이후 날짜, 올바른 시간 범위를 선택하세요.') from None
    params = dict(depPlaceId=departure, arrPlaceId=arrival, depPlandTime=date.strftime('%Y%m%d'))
    if values.get('train_type'):
        params['trainGradeCode'] = values['train_type']
    return params, start, end


@app.errorhandler(APIError)
def api_error(error):
    return jsonify(error=error.info), 400 if error.info['kind'] == 'INVALID_INPUT' else 502


@app.after_request
def log_request(response):
    logging.getLogger('app').info('route=%s status=%s', request.url_rule, response.status_code)
    return response


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/health')
def health():
    import os
    return jsonify(service='tago-train', status='OK', pid=os.getpid())


@app.get('/cities')
def cities():
    return jsonify(items=get('GetCtyCodeList'))


@app.get('/stations')
def stations():
    code = request.args.get('city_code', '')
    if not code.isdigit():
        raise APIError('INVALID_INPUT', '출발 또는 도착 지역을 선택하세요.')
    return jsonify(items=get('GetCtyAcctoTrainSttnList', cityCode=code))


@app.get('/train-types')
def train_types():
    return jsonify(items=get('GetVhcleKndList'))


@app.get('/search')
def search():
    params, start, end = validate(request.args)
    rows = get('GetStrtpntAlocFndTrainInfo', **params)
    result = []
    try:
        for row in rows:
            departure = datetime.strptime(str(row['depplandtime']), '%Y%m%d%H%M%S')
            arrival = datetime.strptime(str(row['arrplandtime']), '%Y%m%d%H%M%S')
            if start <= departure.time().replace(second=0) <= end:
                result.append(dict(train_type=row['traingradename'], train_number=row['trainno'],
                                   departure=row['depplacename'], departure_time=departure.isoformat(' '),
                                   arrival=row['arrplacename'], arrival_time=arrival.isoformat(' ')))
    except (KeyError, ValueError, TypeError):
        raise APIError('PARSE_ERROR', '시간표 필드 형식이 올바르지 않습니다.') from None
    result.sort(key=lambda row: row['departure_time'])
    return jsonify(items=result, status='OK' if result else 'NO_DATA')


if __name__ == '__main__':
    # Werkzeug access logs contain raw query strings, so use the safe route logger above.
    logging.getLogger('werkzeug').disabled = True
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, load_dotenv=False)
