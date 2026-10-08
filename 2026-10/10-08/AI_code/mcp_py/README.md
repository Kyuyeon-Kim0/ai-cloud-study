# Python MCP 서버 실습

학습 날짜: 2026-10-08 (목)

Python으로 MCP 서버의 Tool, Resource, Prompt를 만들고 클라이언트에서 호출하는 실습입니다. 타입 힌트와 Pydantic을 이용한 입력 검증, CSV 매출 처리, OpenAI API를 이용한 요약을 연습합니다.

## 주요 기능

| 서버 | 기능 |
| --- | --- |
| `hello_server.py` | 이름으로 인사, 현재 시각 조회, 지정 날짜까지 남은 일수 안내 |
| `hint_server.py` | 타입 힌트가 있는 덧셈과 없는 덧셈의 스키마·호출 결과 비교 |
| `sales_server.py` | 지역별 매출 합계, 매출 순위, 매출 추가, CSV 리소스, 보고서 프롬프트 |
| `ai_server.py` | OpenAI API로 한국어 요약 생성 |

`hello`의 `dday`는 `target`을 `YYYY-MM-DD` 형식으로 받으며, 현재 구현은 `N일 남았습니다!!` 문자열을 반환합니다. 날짜와 시각은 서버가 실행되는 컴퓨터의 로컬 시간을 기준으로 계산합니다.

## 준비 사항

- Windows PowerShell과 Python. 기존 가상환경에서 확인한 Python 버전은 `3.12.10`입니다.
- AI 요약 실습에는 OpenAI API 키와 사용할 모델 ID가 필요합니다.
- 기본 인사·타입 힌트·매출 실습에는 API 키가 필요하지 않습니다.

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `hello_server.py`, `hint_server.py` | 기본 도구와 타입 힌트 실습 서버 |
| `sales_server.py` | 매출 도구, 리소스, 프롬프트 제공 |
| `ai_server.py` | 요약 도구 제공 |
| `try_hello.py`, `try_hint.py` | 도구 목록·스키마 조회 및 호출 예제 |
| `try_sales.py` | 정상 입력과 오류 입력 비교, 매출 추가 예제 |
| `try_resources.py` | 리소스·리소스 템플릿·프롬프트 조회 예제 |
| `try_ai.py` | 요약 도구 호출 예제 |
| `list_models.py` | API 키로 접근 가능한 모델 ID 조회 |
| `test_sales_server.py` | 임시 CSV 복사본으로 매출 기능 검증 |
| `sales.csv` | 지역과 금액(만원) 데이터 |
| `.gitignore` | 가상환경, 캐시, 비밀 설정 등 Git 제외 규칙 |

## 설치 및 실행

프로젝트 폴더에서 PowerShell로 실행합니다.

```powershell
cd C:\ai-starter\2026-10\10-08\AI_code\mcp_py
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "mcp==2.3.0" "pydantic==2.13.5" "openai==3.26.0" "python-dotenv==1.2.4" "pytest==9.1.1" anyio
```

패키지 버전은 기존 가상환경에서 확인한 값입니다. 이 코드는 `mcp.server.mcpserver.MCPServer`와 `mcp.Client`를 사용하므로 다른 SDK 버전에서는 인터페이스가 다를 수 있습니다.

기본 실습은 다음 명령으로 실행합니다. 각 예제는 서버 객체를 가져와 클라이언트에서 호출하므로 별도 서버 프로세스를 먼저 실행할 필요가 없습니다.

```powershell
python try_hello.py
python try_hint.py
python try_resources.py
```

매출 추가와 오류 처리 예제는 다음 명령으로 실행합니다.

```powershell
python try_sales.py
```

`try_sales.py`는 실행할 때마다 실제 `sales.csv`에 부산 매출 50만원을 추가합니다. `broken` 도구는 오류 응답 확인을 위해 의도적으로 예외를 발생시킵니다.

서버를 직접 실행하려면 다음처럼 실행합니다.

```powershell
python hello_server.py
```

서버는 MCP 클라이언트의 요청을 기다립니다. 종료는 `Ctrl+C`로 합니다.

## 매출 데이터

`sales.csv`는 UTF-8(BOM 없음)으로 저장하고, 첫 줄에 `지역,금액` 헤더를 둡니다.

```csv
지역,금액
서울,120
부산,80
대구,95
서울,30
```

위 내용은 초기 데이터 예시입니다. 매출 추가 도구를 호출하면 실제 파일의 행 수와 합계가 달라집니다.

- `region_total`: 서울·부산·대구 중 한 지역의 매출 합계 반환
- `top_regions`: 매출 합계가 큰 지역부터 `n`개 반환 (`1 ≤ n ≤ 3`)
- `add_sale`: 등록된 지역의 0 이상 금액을 추가하고 전체 건수 반환
- `sales://csv`: 원본 CSV 제공
- `sales://region/{region}`: 해당 지역의 행을 헤더 없이 제공
- `sales_report`: 지역과 문체를 받아 보고서 작성 지시문 제공

## AI 요약 실습

프로젝트 폴더에 `.env`를 만들고 다음 변수에 실제 값을 설정합니다. 아래 값은 형식 예시입니다.

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=your-model-id
```

```powershell
python list_models.py
python try_ai.py
```

`list_models.py` 출력에서 계정으로 접근 가능한 모델 ID를 확인할 수 있습니다. 요약 호출에는 Responses API를 지원하는 모델을 설정해야 합니다. `try_ai.py`는 실제 API 요청을 보냅니다.

`.env`는 Git에서 제외됩니다. 공유용 환경 변수 예시는 실제 키를 제거한 `.env.example`로 작성합니다.

## 테스트

```powershell
python -m pytest test_sales_server.py -q
```

테스트는 임시 CSV 복사본을 사용합니다. 서울 합계 테스트는 원본 데이터의 서울 매출 합계가 150만원인 상태를 전제로 합니다.

## 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| `ModuleNotFoundError` 또는 SDK import 오류 | 가상환경 활성화 여부와 위 설치 명령의 패키지 버전 확인 |
| CSV를 읽을 때 `KeyError` 발생 | 헤더가 `지역,금액`인지, UTF-8(BOM 없음)으로 저장했는지 확인 |
| 매출 합계가 예시와 다름 | `try_sales.py` 실행으로 추가된 행 확인 |
| API 키 또는 모델 설정 오류 | `.env`의 `OPENAI_API_KEY`, `OPENAI_MODEL` 확인 |
| 서버 직접 실행 후 출력 없이 대기 | MCP 클라이언트 요청을 기다리는 상태이며, `try_*.py`로 호출 예제 실행 |
