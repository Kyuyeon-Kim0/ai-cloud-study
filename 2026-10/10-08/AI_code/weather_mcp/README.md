# Weather MCP 서버

학습 날짜: 2026-10-08 (목)

Open-Meteo의 도시 검색·날씨 API를 호출하는 Python MCP 서버입니다. Codex에서 `get_current_weather` 도구를 사용해 도시별 현재 날씨를 조회하고 비교하는 실습입니다.

## 주요 기능

- 한국어 또는 영어 도시 이름으로 위치 검색
- 기온, 체감 온도, 습도, 풍속과 한국어 날씨 설명 반환
- 조회 지역의 국가, 시간대와 API가 제공하는 현재 날씨 시각 반환
- 잘못된 도시 입력, 검색 결과 없음, 타임아웃, HTTP·네트워크 오류 처리

도시 검색 결과 중 첫 번째 위치를 사용합니다. 같은 이름의 도시가 여러 개라면 반환된 도시와 국가를 확인하세요. 현재 코드는 API 키를 사용하지 않습니다.

## 준비 사항

- Windows PowerShell
- Python 3.12 (기존 가상환경: `3.12.10`)
- 인터넷 연결
- Codex CLI: Codex 연동 실습 시 필요
- Node.js와 `npx`: MCP Inspector 실행 시 필요

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `server.py` | API 호출, 입력 검증, 날씨 도구 등록, stdio 서버 실행 |
| `README.md` | 설치·실행 및 Codex 등록 안내 |

## 설치 및 실행

PowerShell에서 프로젝트 폴더로 이동합니다. 가상환경이 이미 있다면 생성 명령을 건너뛰고 활성화합니다.

```powershell
cd C:\ai-starter\2026-10\10-08\AI_code\weather_mcp
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "mcp[cli]==2.3.0" "httpx==0.28.1"
```

이 프로젝트는 MCP 2.x의 `MCPServer`를 사용합니다.

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Weather Tools")
```

서버를 직접 실행하려면 다음 명령을 사용합니다.

```powershell
python server.py
```

stdio 방식으로 MCP 클라이언트 요청을 기다립니다. 웹페이지를 제공하는 서버가 아니므로 브라우저 접속 주소는 없습니다. 직접 실행한 프로세스는 `Ctrl+C`로 종료합니다. Codex에 등록하면 Codex가 서버를 실행하므로 별도 실행이 필요하지 않습니다.

## MCP Inspector로 확인

가상환경을 활성화한 상태에서 실행합니다.

```powershell
mcp dev server.py
```

터미널에 표시되는 Inspector 주소와 연결 정보를 사용합니다. 연결 후 도구 목록에서 `get_current_weather`를 선택하고 다음 입력으로 호출합니다.

```json
{
  "city": "서울"
}
```

## 도구 입력과 반환값

`get_current_weather(city: str) -> dict`는 공백 제거 후 2~50글자인 도시 이름을 받습니다. 예: `서울`, `부산`, `Tokyo`, `New York`.

| 반환 필드 | 내용 |
| --- | --- |
| `success` | 처리 성공 여부 |
| `city`, `country` | 검색된 도시와 국가 |
| `timezone` | 조회 지역의 시간대 |
| `observed_at` | API의 현재 날씨 데이터 시각 |
| `weather` | 날씨 코드에 대응하는 한국어 설명 |
| `temperature` | 단위가 포함된 기온 문자열 |
| `apparent_temperature` | 단위가 포함된 체감 온도 문자열 |
| `humidity` | 단위가 포함된 습도 문자열 |
| `wind_speed` | 단위가 포함된 풍속 문자열 |

입력 오류 등 코드에서 처리한 실패는 다음 형태로 반환합니다.

```json
{
  "success": false,
  "message": "도시 이름은 두 글자 이상 입력하세요."
}
```

이 실패는 도구가 반환한 데이터이므로 응답의 `success` 값을 확인해야 합니다.

## Codex 등록

PowerShell에서 서버의 Python 실행 파일과 스크립트를 절대 경로로 등록합니다.

```powershell
codex mcp add weather-tools -- "C:\ai-starter\2026-10\10-08\AI_code\weather_mcp\.venv\Scripts\python.exe" "C:\ai-starter\2026-10\10-08\AI_code\weather_mcp\server.py"
codex mcp list
codex
```

다른 경로에 프로젝트를 복사했다면 두 경로를 함께 수정합니다. Codex 터미널 화면에서 `/mcp`로 연결 상태를 확인하고 다음처럼 요청합니다.

```text
weather-tools의 get_current_weather 도구로 서울 현재 날씨를 확인해줘.
```

```text
get_current_weather 도구로 서울과 부산의 현재 날씨를 각각 조회해서 비교해줘.
```

CLI 등록은 기본적으로 사용자 `~/.codex/config.toml`에 저장됩니다. 프로젝트에만 설정하려면 신뢰된 프로젝트의 `.codex/config.toml`에 아래 설정을 추가하는 방법도 있습니다. 두 방법 중 하나를 선택합니다.

```toml
[mcp_servers.weather-tools]
command = 'C:\ai-starter\2026-10\10-08\AI_code\weather_mcp\.venv\Scripts\python.exe'
args = ['C:\ai-starter\2026-10\10-08\AI_code\weather_mcp\server.py']
```

설정을 바꾼 뒤 Codex CLI를 다시 시작합니다. IDE 확장에서는 MCP 설정을 저장한 뒤 확장을 재시작합니다. 등록과 환경 변수 전달 방법은 [공식 OpenAI MCP 문서](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)를 참고하세요.

## API 키가 필요한 서비스로 확장

현재 날씨 서버에는 아래 설정이 필요하지 않습니다. API 키를 요구하는 다른 서비스를 연결할 때 Python에서 환경 변수를 읽을 수 있습니다.

```python
import os

API_KEY = os.getenv("COMPANY_API_KEY")
if not API_KEY:
    raise RuntimeError("COMPANY_API_KEY 환경변수가 없습니다.")
```

Codex 설정의 해당 서버 항목에 변수 전달을 추가합니다.

```toml
env_vars = ["COMPANY_API_KEY"]
```

같은 PowerShell 세션에서 값을 설정하고 Codex를 시작합니다. 아래 키는 자리 표시자입니다.

```powershell
$env:COMPANY_API_KEY = "your-api-key"
codex
```

`env_vars`는 Codex 실행 환경에서 해당 변수를 읽어 MCP 서버로 전달합니다. 실제 API 키는 소스 코드나 README에 기록하지 않습니다.

## 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| `No module named 'mcp.server.fastmcp'` | MCP 2.x에서는 `MCPServer` import와 생성자를 사용 |
| `mcp` 명령을 찾을 수 없음 | 가상환경 활성화와 `mcp[cli]` 설치 확인 |
| Inspector 실행 실패 | Node.js·`npx` 설치 여부와 터미널 오류 확인 |
| Codex에서 서버 실행 실패 | 등록된 Python·스크립트 경로와 패키지 설치 확인 |
| 도시 검색 결과 없음 | 영어 이름으로 다시 조회하거나 철자 확인 |
| 타임아웃 또는 네트워크 오류 | 인터넷 연결과 Open-Meteo 접근 상태 확인; 요청별 제한 시간은 10초 |
| Python 직접 실행 후 출력 없이 대기 | stdio 요청을 기다리는 상태이므로 Inspector 또는 Codex에서 호출 |

## 사용 API

- 도시 검색: `https://geocoding-api.open-meteo.com/v1/search`
- 날씨 조회: `https://api.open-meteo.com/v1/forecast`
