# poke-lab

대용량 포켓몬 데이터를 대상으로 CSV 처리 방식, `pandas`, SQLite, 외부 API 캐시의 사용법과 성능을 비교해 보는 Python 실습 프로젝트입니다.

가상의 포켓몬 데이터 최대 100만 건을 만들고, 읽기·필터·집계·개수 세기 작업을 여러 방식으로 실행하며 경과 시간, 메모리 변화, CPU 사용률을 기록합니다. 별도로 [PokéAPI](https://pokeapi.co/)에서 실제 포켓몬 정보를 받아 캐시하고, Streamlit 대시보드로 데이터를 탐색할 수 있습니다.

## 주요 기능

- 1천 / 10만 / 100만 건의 재현 가능한 가상 포켓몬 CSV 생성
- 기본 Python `csv`와 `pandas` 기반의 읽기, 개수 세기, 필터, 그룹 집계 비교
- `psutil`로 실행 시간·메모리·CPU 사용률을 `logs/resource_log.csv`에 기록
- 집계 결과를 CSV와 JSON으로 저장
- PokéAPI 호출, 예외 처리, 로컬 JSON 캐시 예제
- CSV를 SQLite DB로 적재하고 조회 성능 비교
- Streamlit 기반 데이터 탐색 대시보드

## 요구 사항

- Python 3.10 이상 권장
- 인터넷 연결: PokéAPI 호출 예제를 처음 실행할 때만 필요

## 설치

프로젝트 폴더에서 가상환경을 만들고 의존성을 설치합니다.

```powershell
cd 2026-09/09-15/poke-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

PowerShell 실행 정책으로 가상환경 활성화가 막히면, 활성화하지 않고 `.venv\Scripts\python.exe`로 아래 명령을 실행해도 됩니다.

## 빠른 시작

데이터 파일이 없다면 먼저 생성합니다. 기존 파일은 같은 이름으로 다시 생성됩니다.

```powershell
python make_data.py
```

그 다음 원하는 예제를 실행합니다.

```powershell
# pandas로 유형별 집계 후 결과 파일 저장
python save_result.py

# CSV / pandas 집계 성능 비교
python compare_all.py

# Streamlit 대시보드 실행
streamlit run dashboard.py
```

대시보드는 기본적으로 `data/pokemon_1m.csv`를 읽습니다. 실행 후 터미널에 표시된 로컬 주소를 브라우저에서 엽니다.

## 스크립트 안내

| 파일 | 설명 |
| --- | --- |
| `make_data.py` | 가상 포켓몬 CSV 3종(1천·10만·100만 행)을 생성합니다. |
| `read_basic.py`, `read_pandas.py` | `csv`와 `pandas`로 파일을 읽는 기본 예제입니다. |
| `count_basic.py`, `count_pandas.py`, `count_measured.py` | 행 수를 세고 방식별 자원 사용량을 측정합니다. |
| `filter_basic.py`, `filter_measured.py` | 조건 필터링 예제와 측정 예제입니다. |
| `group_basic.py` | 유형별 그룹 집계 기본 예제입니다. |
| `compare_all.py` | 스트리밍 CSV, 전체 CSV 리스트, 일반 pandas, 최적화 pandas 집계를 비교합니다. |
| `save_result.py` | 유형별 건수·평균 공격력·최대 HP를 `output/`에 저장합니다. |
| `measure.py` | 경과 시간, 메모리, CPU 측정 및 CSV 로그 저장 유틸리티입니다. |
| `call_basic.py`, `call_safe.py` | PokéAPI 단일 호출 및 오류 처리 예제입니다. |
| `cache_file.py` | PokéAPI의 처음 50개 포켓몬을 내려받아 JSON으로 캐시하고 CSV로 변환합니다. |
| `dbload.py` | 100만 건 CSV를 SQLite로 적재하고 집계·COUNT 성능을 확인합니다. |
| `dashboard.py` | 필터, 요약 지표, 차트, 상위 공격력 표를 제공하는 Streamlit 앱입니다. |

## 추가 실행 예시

```powershell
# API 호출 및 로컬 캐시 생성/재사용
python cache_file.py

# CSV → SQLite 적재, 결과 조회, CSV와 DB COUNT 비교
python dbload.py

# 기본 API 오류 처리 예제
python call_safe.py
```

`dbload.py`는 실행할 때마다 `data/pokemon.db`를 새로 생성합니다.

## 데이터와 결과물

```text
data/
├── pokemon_1k.csv       # 가상 데이터 1,000건
├── pokemon_100k.csv     # 가상 데이터 100,000건
├── pokemon_1m.csv       # 가상 데이터 1,000,000건
├── pokemon_api.json     # PokéAPI 캐시
├── pokemon_api.csv      # 캐시를 변환한 CSV
└── pokemon.db           # SQLite 적재 결과

logs/resource_log.csv    # 성능 측정 로그
output/summary.csv       # 유형별 집계 결과
output/summary.json      # 유형별 집계 결과(JSON)
```

가상 데이터는 고정 시드(`42`)를 사용하므로, 같은 코드로 생성하면 동일한 데이터 분포를 재현할 수 있습니다. 성능 측정값은 PC 사양, 운영체제 파일 캐시, 실행 시점의 부하에 따라 달라질 수 있습니다.

## 라이선스 및 데이터 출처

이 저장소의 대용량 CSV는 실습용으로 생성한 가상 데이터입니다. API 예제는 [PokéAPI](https://pokeapi.co/)를 사용하며, 서비스 이용 시 해당 API의 정책을 따라야 합니다.
