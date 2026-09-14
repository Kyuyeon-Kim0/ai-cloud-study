# TASK.md

## 작업 목적
공공데이터 열차정보 API의 4개 상세 기능을 이용해 Flask 기반 기차 시간표 조회 웹페이지를 만든다.

## 사용 API

1. `/GetCtyCodeList` - 도시코드 목록
2. `/GetCtyAcctoTrainSttnList` - 시/도별 기차역 목록
3. `/GetVhcleKndList` - 차량종류 목록
4. `/GetStrtpntAlocFndTrainInfo` - 출/도착지 기반 열차정보

Base URL:

```text
https://apis.data.go.kr/1613000/TrainInfo
```

## 사용자 화면

```text
출발 지역   [선택]
출발역      [선택]
도착 지역   [선택]
도착역      [선택]
열차 종류   [선택]
조회 날짜   [달력]
시작 시간   [시간]
종료 시간   [시간]

[조회]
```

결과표:

- 열차 종류
- 열차번호
- 출발역
- 출발시간
- 도착역
- 도착시간

## 기술 구성

- Python
- Flask
- requests
- python-dotenv
- HTML / CSS / JavaScript

## 프로젝트 구조

```text
train-timetable/
├─ app.py
├─ api_client.py
├─ health_check.py
├─ agent.py
├─ requirements.txt
├─ .env
├─ .env.example
├─ .gitignore
├─ TASK.md
├─ AGENT_WORKFLOW.md
├─ templates/
│  └─ index.html
├─ static/
│  ├─ style.css
│  └─ app.js
└─ logs/
   ├─ app.log
   └─ agent.log
```

## Flask 엔드포인트

### GET `/cities`
`GetCtyCodeList` 호출 후 도시 목록 반환.

### GET `/stations?city_code=...`
`GetCtyAcctoTrainSttnList` 호출 후 해당 도시의 역 목록 반환.

### GET `/train-types`
`GetVhcleKndList` 호출 후 차량종류 목록 반환.

### GET `/search`
입력값:

- `departure`
- `arrival`
- `date`
- `start_time`
- `end_time`
- `train_type` (선택)

`GetStrtpntAlocFndTrainInfo`를 호출하고 시간 범위로 필터링하여 반환한다.

## 화면 동작 순서

1. 페이지 로드 시 `/cities`, `/train-types` 호출
2. 출발 지역 선택 시 해당 도시의 `/stations` 호출
3. 도착 지역 선택 시 해당 도시의 `/stations` 호출
4. 역/열차종류/날짜/시간 선택
5. 조회 버튼 클릭
6. `/search` 호출
7. 결과를 HTML 테이블에 표시

## 인증키

`.env`:

```text
SERVICE_KEY=발급받은_인증키
```

`.env.example`:

```text
SERVICE_KEY=YOUR_SERVICE_KEY
```

`.gitignore`:

```text
.env
__pycache__/
*.pyc
logs/*.log
```

인증키를 Python, HTML, JavaScript, 로그, 오류 응답에 직접 노출하지 않는다.

## 입력 검증

- 출발/도착 지역 및 역 필수
- 출발역 != 도착역
- 날짜는 오늘 이후
- 시작시간 <= 종료시간
- 열차종류는 선택값

## 오류 처리

다음을 구분한다.

- `NETWORK_ERROR`
- `HTTP_ERROR`
- `AUTH_ERROR`
- `API_ERROR`
- `PARSE_ERROR`
- `NO_DATA`
- `INVALID_INPUT`

개발 화면에는 사용자 메시지, HTTP 상태, API 코드, API 메시지를 표시할 수 있지만 인증키는 절대 표시하지 않는다.

## 구현 순서

1. `.env`, requirements, 기본 구조 생성
2. `api_client.py` 공통 GET 함수 구현
3. 도시코드 조회 테스트
4. 시/도별 역 목록 조회 테스트
5. 차량종류 조회 테스트
6. 시간표 조회 테스트
7. 실제 JSON 필드 확인 및 매핑
8. Flask `/cities` 구현
9. Flask `/stations` 구현
10. Flask `/train-types` 구현
11. Flask `/search` 구현
12. `index.html` 연동
13. 시간 범위 필터 구현
14. 오류 처리
15. 정상/장애 테스트
16. Agent health check 연동

## 구현 원칙

- 먼저 API 단독 테스트 후 Flask를 연결한다.
- API 호출은 `api_client.py`에 모은다.
- 웹 로직과 Agent 운영 로직을 분리한다.
- 불필요한 라이브러리를 추가하지 않는다.
- pandas는 단독 테스트 스크립트에서만 사용해도 된다.
- Flask API 응답은 기본 Python 자료형/JSON으로 처리한다.
- 자동 복구는 허용된 범위에서 1회만 수행한다.

## 완료 조건

- 도시 목록 조회 가능
- 도시 선택 후 역 목록 변경 가능
- 차량종류 목록 조회 가능
- 날짜/시간 범위 지정 가능
- 시간표 조회 가능
- 결과 6개 컬럼 표시
- 입력 오류 처리 가능
- API 오류 상세 진단 가능
- 인증키 노출 없음
- Agent가 4개 API 기능을 개별 점검 가능
