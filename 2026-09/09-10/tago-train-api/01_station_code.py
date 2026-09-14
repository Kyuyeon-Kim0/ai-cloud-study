"""도시, 역, 차량종류 단독 점검. 인증키와 원본 오류 본문은 출력하지 않습니다."""
import json
from api_client import APIError, get

if __name__ == '__main__':
    for operation, params in [
        ('GetCtyCodeList', {}),
        ('GetCtyAcctoTrainSttnList', {'cityCode': '11'}),
        ('GetVhcleKndList', {}),
    ]:
        try:
            print(operation, json.dumps(get(operation, **params), ensure_ascii=False, indent=2))
        except APIError as error:
            print(json.dumps(error.info, ensure_ascii=False))
