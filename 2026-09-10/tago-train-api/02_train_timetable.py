"""서울-부산 오늘 시간표 단독 점검."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from api_client import APIError, get

DEP = 'NAT010000'
ARR = 'NAT014445'
DATE = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d')
TRAIN_TYPE = None

if __name__ == '__main__':
    params = dict(depPlaceId=DEP, arrPlaceId=ARR, depPlandTime=DATE)
    if TRAIN_TYPE:
        params['trainGradeCode'] = TRAIN_TYPE
    try:
        print(json.dumps(get('GetStrtpntAlocFndTrainInfo', **params), ensure_ascii=False, indent=2))
    except APIError as error:
        print(json.dumps(error.info, ensure_ascii=False))
