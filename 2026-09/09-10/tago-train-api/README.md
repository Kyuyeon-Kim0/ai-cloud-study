# TAGO 기차 시간표와 운영 에이전트

학습 날짜: 2026-09-10 (목)

TASK.md 및 AGENT_WORKFLOW.md에 따라 구성한 Flask 서비스와 규칙 기반 운영 에이전트입니다. LLM이나 별도 OpenAI 키는 필요하지 않습니다.

## 실행 (PowerShell)

```powershell
cd C:\ai-starter\2026-09\09-10\tago-train-api
.\.venv\Scripts\python.exe app.py
```

화면: http://127.0.0.1:5000

다른 터미널에서 점검만 실행:

```powershell
.\.venv\Scripts\python.exe agent.py
```

중단된 서비스 시작과 API별 최대 1회 재시도 허용:

```powershell
.\.venv\Scripts\python.exe agent.py --recover
```

조회 조건을 바꾼 점검:

```powershell
.\.venv\Scripts\python.exe agent.py --city-code 11 --departure NAT010000 --arrival NAT014445 --date 2026-09-28 --start-time 09:00 --end-time 18:00
```

기본 날짜는 한국 기준 오늘입니다. 종료 코드는 ERROR일 때 1, 그 외에는 0입니다. 복구로 시작한 서비스는 점검 종료 후에도 실행됩니다. 다른 프로그램이 5000번 포트를 사용하면 종료하거나 포트를 바꾸지 않고 오류로 보고합니다. 응답하지 않지만 포트를 점유하는 프로세스는 자동 종료하지 않습니다.

## 파일 역할

- api_client.py: 인증, 4개 API 공통 호출, JSON/XML 인증 오류 판별, 페이지 처리
- app.py: Flask 웹 및 JSON 엔드포인트, 입력 검증, 시간 필터
- health_check.py: 환경·서비스·포트·DNS·API 점검 함수
- agent.py: 점검 → 판단 → 1회 조치 → 재검증 → JSON 보고
- templates/index.html, static/: 기차 시간표 화면
- test_agent.py: 네트워크를 사용하지 않는 단위 테스트
- 01_station_code.py, 02_train_timetable.py: 공통 클라이언트를 사용하는 단독 API 확인

## 설정과 설치

기존 .env의 SERVICE_KEY를 사용하며 UTF-8과 UTF-16을 지원합니다. 인증키는 화면·오류 응답·로그에 출력하지 않습니다. 외부 API 원본 오류 메시지 대신 안전한 메시지와 HTTP 상태/API 코드를 제공합니다.

이 PC에는 .venv 실행환경을 준비했습니다. 다른 PC에서는 Python 3.10 이상 설치 후:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

.env가 없다면 .env.example을 복사하고 인증키를 입력하세요. 운영 에이전트 자체는 패키지 설치, .env 변경, 시스템 설정 변경을 하지 않습니다.

## 상태와 로그

- OK: 로컬 서비스와 필수 API 정상
- WARNING: 조회 결과 없음 또는 응답 지연
- ERROR: 서비스/API 지속 실패, 인증 오류, 환경 또는 입력 오류
- RECOVERED: 허용된 조치 후 재검증 성공

각 API 결과는 독립적으로 보고하며 인증 오류는 재시도하지 않습니다. DNS 실패 시 하위 API는 SKIPPED로 기록합니다. API 재시도와 서비스 시작은 한 실행에서 각각 최대 1회입니다. 복구 후 로컬 프로세스 응답, 포트, 화면 및 JSON 엔드포인트를 다시 검증합니다. `/health`의 PID로 서비스 프로세스의 응답을 확인하며 OS 전체 프로세스 목록을 수집하지 않습니다.

logs/app.log에는 경로·HTTP 상태·API 코드·응답시간을, logs/agent.log에는 점검과 복구 결과를 기록합니다. 로그는 파일당 1MB, 백업 3개로 제한합니다. 임의 로그 내용은 인증정보 유출 방지를 위해 보고서에 복사하지 않습니다.

## 검증

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

실제 API 연결에는 공공데이터 API 접근이 가능한 네트워크와 유효한 인증키가 필요합니다. 화면의 날짜는 오늘을 포함하며 시간 필터는 출발시간 기준입니다. 빈 결과는 정상 응답으로 표시합니다. Flask 내장 서버는 로컬 개발용입니다.
