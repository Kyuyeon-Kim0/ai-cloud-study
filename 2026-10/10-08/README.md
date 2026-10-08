# 2026-10-08 (목) 학습 기록

## 학습 주제

- Python MCP 서버 구현과 클라이언트 연동
- Tool, Resource, Prompt의 역할과 호출 방법
- 타입 힌트와 Pydantic을 이용한 입력 검증
- 외부 API를 사용하는 날씨 도구 구현과 Codex 등록
- FastAPI와 MySQL을 이용한 재고 관리 API 및 웹 대시보드 구현
- 트랜잭션·행 잠금과 실제 MySQL을 사용하는 통합 테스트

## 핵심 이해

### MCP 서버와 클라이언트

- 서버에 도구를 등록하고 클라이언트에서 목록을 조회하거나 이름과 인자로 호출한다.
- Tool은 기능 실행, Resource는 데이터 제공, Prompt는 재사용할 지시문 제공에 사용한다.
- `client.list_tools()`로 도구 목록을 조회하고, 반환 모델의 `model_dump_json()`으로 JSON을 출력할 수 있다.
- 이번 실습 환경의 MCP 2.x에서는 `FastMCP` 대신 `MCPServer`를 사용한다.

### 타입 힌트와 입력 검증

- 함수의 타입 힌트와 설명으로 도구의 입력·출력 스키마를 구성한다.
- `Literal`로 허용 지역을 제한하고, `Field`로 금액과 조회 개수의 범위를 지정한다.
- 정상 입력, 잘못된 입력, 의도적인 예외를 비교하며 오류 응답을 확인한다.

### CSV와 외부 API

- CSV 파일에는 실행 명령이 아닌 헤더와 데이터 행을 저장한다.
- 지역별 매출을 집계하고 원본 CSV 또는 지역별 행을 리소스로 제공한다.
- 날씨 도구는 도시 이름을 좌표로 변환한 뒤 현재 날씨를 조회한다.
- 외부 API 호출에서는 입력 검증, 타임아웃, HTTP 오류와 네트워크 오류를 처리한다.
- API 키는 환경 변수로 관리하고 `.env`와 가상환경은 Git에서 제외한다.

### Codex 연동

- stdio MCP 서버는 Python 실행 파일과 서버 스크립트 경로로 등록한다.
- `codex mcp list`로 등록 목록을 확인하고 Codex CLI의 `/mcp`로 연결 상태를 확인한다.
- MCP 서버가 API 키를 필요로 하면 `env_vars`로 실행 환경의 변수를 전달할 수 있다.

### 재고 관리 API 구조

- FastAPI의 진입점, 라우터, 서비스, DB 연결과 설정을 파일별로 분리한다.
- Pydantic Settings로 환경 변수를 읽고 MySQL 상품 조회 결과를 API로 반환한다.
- 상품 관리, 입출고 이력, 재고 현황을 제공하며 동시 출고와 실패 시 롤백을 MySQL에서 검증한다.
- 금액은 `DECIMAL`로 저장하고 수량은 정수로 검증한다. 재고 변경과 이력 기록을 하나의 트랜잭션으로 처리한다.
- 입출고 시 `SELECT ... FOR UPDATE`로 상품 행을 잠가 동시 출고로 재고가 음수가 되는 것을 방지한다.
- 재고가 남은 상품은 삭제를 막고, 재고가 0인 상품은 목록에서 제외하면서 입출고 이력을 보존한다.
- 기존 상품을 유지하며 스키마를 보완하고, 자동 테스트는 별도의 임시 MySQL에서 실행한다.

## 실습 내용

- 인사, 현재 시간, 지정 날짜까지 남은 일수 안내 도구 구현
- 타입 힌트 유무에 따른 덧셈 도구의 스키마와 호출 결과 비교
- CSV 매출 합계·순위·추가 도구와 보고서 프롬프트 구현
- 임시 CSV 복사본을 사용하는 매출 테스트 작성
- OpenAI API를 이용한 요약 도구와 호출 예제 작성
- Open-Meteo 날씨 도구 구현 및 Codex 등록 방법 정리
- MCP SDK 버전 차이로 발생한 import 오류 수정
- 프로젝트 README와 Git 제외 설정 정리
- FastAPI·MySQL 상품 등록·조회·수정·삭제 API 구현
- 입출고 사유·처리 후 재고 기록과 안전 재고 이하 상품 조회 구현
- 검색·페이지 조회·재고 현황 요약과 웹 대시보드 추가
- 기존 상품 3건을 보존하면서 재고 열과 입출고 테이블 추가
- 임시 MySQL에서 통합 테스트 9개 통과: 상품 관리, 입력 검증, 동시 출고, 롤백, 스키마 마이그레이션 등

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [AI_code/mcp_py/](AI_code/mcp_py/README.md) | MCP 기본 도구, 타입 검증, 매출·AI 요약, 클라이언트 호출 실습 |
| [AI_code/weather_mcp/](AI_code/weather_mcp/README.md) | 날씨 API를 연결하는 MCP 서버와 Codex 연동 실습 |
| [inventory_project/](inventory_project/README.md) | FastAPI·MySQL 상품·재고 관리 API와 웹 대시보드 |
| [inventory_project/app/main.py](inventory_project/app/main.py) | API·웹 화면 제공, DB 상태 확인과 오류 처리 |
| [inventory_project/app/services/product_service.py](inventory_project/app/services/product_service.py) | MySQL 트랜잭션 기반 상품·입출고·재고 집계 |
| [inventory_project/init_db.py](inventory_project/init_db.py) | 기존 상품을 보존하는 테이블 초기화와 스키마 보완 |
| [inventory_project/run_tests.py](inventory_project/run_tests.py) | 임시 MySQL 컨테이너에서 통합 테스트 실행 |

## 실행 방법

- MCP 실습의 설치·실행·Codex 등록은 각 프로젝트 README를 따른다.
- `mcp_py/try_sales.py`는 실제 CSV에 매출을 추가하므로 반복 실행하면 데이터가 달라진다.
- 재고 관리 프로젝트는 실행 중인 MySQL과 `.env`의 연결 정보를 준비한 뒤 아래 명령으로 실행한다. 기존 가상환경이 없다면 먼저 `py -3.12 -m venv .venv`로 생성한다.

```powershell
cd C:\ai-starter\2026-10\10-08\inventory_project
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python init_db.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

웹 화면은 `http://127.0.0.1:8010/dashboard`, API 문서는 `/docs`, DB 상태 확인은 `/health`에서 제공한다. Docker Desktop을 사용하는 자동 테스트와 상세 설치·사용 방법은 [재고 관리 프로젝트 README](inventory_project/README.md)를 따른다.
