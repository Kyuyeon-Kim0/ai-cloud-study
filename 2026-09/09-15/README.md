# 2026-09-15 (월) 웹·데이터·시스템 모니터링 실습

정적/동적 웹의 차이와 데이터 형식·처리 방식에 따른 자원 사용량을 학습하기 위한 실습 모음입니다. 서비스가 실행되고 사용자가 이용하면 어떤 로그가 남으며, CPU·메모리·네트워크 자원이 어떻게 변하는지 관찰하는 것을 목표로 합니다.

## 학습 흐름

```text
정적·동적 웹 이해
        ↓
HTML 게임 실행 및 사용자 활동 기록
        ↓
시스템 자원 모니터링
        ↓
CSV·JSON 읽기 방식 비교 및 장비 현황 API
        ↓
대용량 포켓몬 데이터 처리·API 캐시·SQLite·대시보드
```

## 구성

| 폴더/파일 | 내용 |
| --- | --- |
| `09.15_교안_정적,동적html이해_자료에따른 자원차이/` | 정적·동적 웹, CSV/pandas, 포켓몬 데이터, API·대시보드, 운영 판단을 다루는 HTML 교안 6종 |
| `html_game/` | 브라우저 클릭 게임, 사용자 행동 로그, PC 시스템 자원 모니터링 실습 |
| `web-lab/` | CSV 기반 장비 점검 현황 API와 화면, CSV/JSON 읽기 성능 비교 실습 |
| `poke-lab/` | 대용량 포켓몬 CSV 처리, 성능 측정, PokeAPI 캐시, SQLite, Streamlit 대시보드 실습 |
| `memo.txt` | SQLite 변환 실습 및 후속 질문 메모 |

## 빠른 시작

각 실습은 해당 하위 폴더에서 실행합니다. Python 3.10 이상을 권장합니다.

```powershell
cd C:\ai-starter\2026-09\09-15
```

### 1. HTML 게임과 시스템 모니터링

`html_game`은 10초 동안 클릭한 결과를 서버에 기록하고, 별도 프로그램으로 PC 전체의 자원 사용량을 1초 단위로 저장합니다.

```powershell
cd html_game
py -m pip install psutil
py server.py
```

다른 PowerShell 창에서 모니터링을 시작합니다.

```powershell
cd C:\ai-starter\2026-09\09-15\html_game
py monitor.py
```

브라우저에서 서버가 출력한 주소(로컬 실행 시 `http://127.0.0.1:8000`)를 엽니다.

- `game_log.csv`: 접속, 시작, 클릭, 종료 등 사용자 행동
- `resource_log.csv`: CPU, 메모리, 송수신량 등 PC 전체 자원 변화

두 로그의 시각을 비교해 사용자 행동과 시스템 상태를 연결해 볼 수 있습니다.

### 2. 장비 현황 웹 API와 파일 읽기 비교

`web-lab`은 `static/data.csv`를 읽어 장비 현황 JSON API와 웹 화면을 제공합니다. CSV를 저장한 뒤 다음 API 요청부터 변경 내용이 반영됩니다.

```powershell
cd web-lab
py -m pip install pandas psutil
py app.py
```

브라우저에서 `http://127.0.0.1:8000`을 열고, API는 `http://127.0.0.1:8000/api/equipment`에서 확인합니다.

동일한 1,000행 데이터를 CSV·JSON·pandas 방식으로 다섯 번씩 읽어 성능을 기록하려면 다음을 실행합니다.

```powershell
py compare_reads.py
```

결과는 `web-lab/logs/resource_log.csv`에 누적됩니다.

### 3. 포켓몬 데이터 처리 실습

`poke-lab`은 1천·10만·100만 건의 재현 가능한 가상 포켓몬 데이터를 사용해 Python 기본 CSV, pandas, SQLite의 처리 방식과 자원 사용량을 비교합니다.

```powershell
cd poke-lab
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

데이터가 없거나 다시 만들려면 다음을 실행합니다. 기존 같은 이름의 CSV는 다시 생성됩니다.

```powershell
py make_data.py
```

자주 사용하는 실행 예시는 다음과 같습니다.

```powershell
# 타입별 집계 결과를 CSV/JSON으로 저장
py save_result.py

# CSV 처리 방식별 성능 비교
py compare_all.py

# PokeAPI 데이터 50건을 로컬 JSON/CSV로 캐시
py cache_file.py

# 100만 행 CSV를 SQLite에 적재하고 조회 성능 비교
py dbload.py

# 대시보드 실행
streamlit run dashboard.py
```

주요 결과물은 다음 위치에 생성·누적됩니다.

| 경로 | 내용 |
| --- | --- |
| `poke-lab/data/` | 생성 CSV, PokeAPI 캐시, SQLite 데이터베이스 |
| `poke-lab/logs/resource_log.csv` | 처리별 실행 시간·메모리·CPU 측정 로그 |
| `poke-lab/output/summary.csv` | 타입별 건수·평균 공격력·최대 HP 집계 |
| `poke-lab/output/summary.json` | 동일 집계의 JSON 형식 |

## 참고

- 성능 측정값은 PC 사양, 실행 시점, 운영체제 파일 캐시와 백그라운드 프로그램에 따라 달라질 수 있습니다.
- `html_game`의 자원 로그는 게임 서버 프로세스만이 아니라 해당 PC 전체의 자원 및 네트워크 사용량입니다.
- PokeAPI 캐시 실습은 최초 실행 시 인터넷 연결이 필요합니다. 데이터 출처는 [PokeAPI](https://pokeapi.co/)입니다.
