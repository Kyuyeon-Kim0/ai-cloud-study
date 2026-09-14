# AGENT_WORKFLOW.md

## 목적
기차시간표 Flask 서비스를 시스템 엔지니어 관점에서 점검하고, 장애를 분류하고, 안전한 범위에서 복구한 뒤 재검증·보고하는 규칙 기반 Agent를 설계한다.

핵심 흐름:

```text
점검 → 판단 → 조치 → 검증 → 보고
```

## 서비스 데이터 흐름

```text
사용자
  ↓
HTML
  ↓
Flask
  ├─ /cities      → GetCtyCodeList
  ├─ /stations    → GetCtyAcctoTrainSttnList
  ├─ /train-types → GetVhcleKndList
  └─ /search      → GetStrtpntAlocFndTrainInfo
                       ↓
                 공공데이터 API
```

## Agent 점검 대상

1. Python 실행환경
2. `.env` 존재 여부 (값은 출력 금지)
3. Flask 프로세스
4. 서비스 포트
5. 로컬 HTTP 응답
6. 인터넷/DNS
7. 공공데이터 Base URL
8. 도시코드 API
9. 시/도별 역 목록 API
10. 차량종류 API
11. 시간표 API
12. JSON 파싱
13. 로그

## WF-01 서비스 시작 점검

- 프로젝트 파일 확인
- `.env` 존재 확인
- 필수 패키지 확인
- Flask 실행
- 포트 LISTEN 확인
- 로컬 HTTP 확인

정상: `SERVICE_OK`

## WF-02 참조정보 API 점검

순서:

```text
GetCtyCodeList
  ↓
GetCtyAcctoTrainSttnList
  ↓
GetVhcleKndList
```

각 API는 독립적으로 상태를 기록한다.

예:

```text
CITY_API=OK
STATION_API=OK
VEHICLE_API=OK
```

## WF-03 시간표 API 점검

`GetStrtpntAlocFndTrainInfo`를 테스트 조건으로 호출한다.

점검:

- HTTP 상태
- API resultCode
- JSON 파싱
- items 존재 여부
- 응답시간

## WF-04 입력 검증

- 출발역/도착역 존재
- 출발역 != 도착역
- 날짜는 오늘 이후
- 시작시간 <= 종료시간
- 열차종류 코드는 선택

실패 시 외부 API를 호출하지 않는다.

## WF-05 장애 분류

```text
SERVICE_DOWN
PORT_CLOSED
NETWORK_ERROR
HTTP_ERROR
AUTH_ERROR
CITY_API_ERROR
STATION_API_ERROR
VEHICLE_API_ERROR
TIMETABLE_API_ERROR
PARSE_ERROR
NO_DATA
UNKNOWN_ERROR
```

## WF-06 장애 진단 순서

```text
Flask 프로세스
  ↓
포트
  ↓
로컬 HTTP
  ↓
DNS/인터넷
  ↓
Base URL
  ↓
도시코드 API
  ↓
역 목록 API
  ↓
차량종류 API
  ↓
시간표 API
  ↓
JSON/로그 확인
```

상위 단계 실패 시 하위 단계 오류를 원인으로 단정하지 않는다.

## WF-07 자동 복구

허용:

- Flask 프로세스 재시작 1회
- API 요청 재시도 1회
- 일시적 네트워크 오류 재확인 1회

금지:

- `.env` 수정
- 인증키 변경
- 패키지 자동 설치
- 방화벽/시스템 설정 변경
- 임의 포트 변경
- 전체 코드 자동 개편

## WF-08 복구 검증

복구 후 반드시 아래 순서로 재검증한다.

```text
프로세스 → 포트 → HTTP → 관련 API → JSON → 화면 요청
```

실패하면 추가 자동 수정 없이 `ERROR`로 보고한다.

## WF-09 로그

`logs/app.log`:
- 웹 요청
- HTTP 상태
- API 상태
- 응답시간

`logs/agent.log`:
- 점검 결과
- 장애 분류
- 복구 시도
- 복구 결과

기록 금지:
- SERVICE_KEY
- 전체 요청 URL에 포함된 인증키
- 민감 환경변수

## WF-10 상태 판정

```text
OK        : 서비스와 필수 API 정상
WARNING   : 서비스 가능, 응답 지연/일시 오류
ERROR     : 서비스 또는 필수 API 지속 실패
RECOVERED : 1회 복구 후 재검증 성공
```

## WF-11 상태 보고 예시

```text
상태: OK
Flask: 정상
Port: 정상
CITY API: 정상
STATION API: 정상
VEHICLE API: 정상
TIMETABLE API: 정상
최근 오류: 없음
복구 수행: 없음
```

## 테스트 시나리오

### TEST-01 정상
모든 서비스/API 정상 → `OK`

### TEST-02 Flask 중단
`SERVICE_DOWN` → 재시작 1회 → 재검증 성공 시 `RECOVERED`

### TEST-03 도시코드 API 실패
`CITY_API_ERROR` → 재시도 1회 → 실패 시 `ERROR`

### TEST-04 역 목록 API 실패
`STATION_API_ERROR` → 사용자 역 선택 불가 → `ERROR`

### TEST-05 차량종류 API 실패
`VEHICLE_API_ERROR` → 열차종류 선택 기능 오류 → `WARNING` 또는 필수 정책에 따라 `ERROR`

### TEST-06 시간표 API 실패
`TIMETABLE_API_ERROR` → 조회 불가 → 재시도 1회 → 실패 시 `ERROR`

### TEST-07 인증 오류
`AUTH_ERROR` → 자동 수정 금지 → 즉시 `ERROR` 보고

### TEST-08 네트워크 오류
`NETWORK_ERROR` → 1회 재확인 → 실패 시 `ERROR`

## 완료 조건

- Flask/포트/HTTP 점검 가능
- 4개 API를 개별 점검 가능
- 장애가 어느 API 단계인지 분류 가능
- 인증키가 로그에 노출되지 않음
- 허용된 복구를 1회만 수행
- 복구 후 재검증 수행
- OK/WARNING/ERROR/RECOVERED 보고 가능
