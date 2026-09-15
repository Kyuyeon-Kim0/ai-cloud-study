# Web Lab

CSV 파일을 장비 점검 현황 API와 웹 화면으로 제공하고, CSV·JSON 읽기 방식의 자원 사용량을 비교하는 Python 실습 프로젝트입니다.

## 구성

- `app.py` — `static/data.csv`를 읽어 `/api/equipment` JSON API와 정적 웹 화면을 제공하는 개발 서버
- `static/index.html` — 장비 상태별 필터와 5초 자동 새로고침을 지원하는 현황 화면
- `static/data.csv` — API가 실제로 읽는 장비 점검 데이터
- `static/data.json` — 파일 형식별 읽기 성능 비교용 데이터
- `compare_reads.py` — 표준 라이브러리와 pandas를 이용한 CSV·JSON 읽기 비교 실행 스크립트
- `measure.py` — 실행 시간, 메모리, CPU 사용량을 `logs/resource_log.csv`에 기록하는 공통 도구

## 요구 사항

- Python 3.10 이상
- 패키지: `pandas`, `psutil`

설치:

```powershell
py -m pip install pandas psutil
```

## 웹 서버 실행

프로젝트 폴더에서 아래 명령을 실행합니다.

```powershell
py app.py
```

브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000)을 엽니다.

- API 엔드포인트: [http://127.0.0.1:8000/api/equipment](http://127.0.0.1:8000/api/equipment)
- 웹 화면은 5초마다 API를 다시 호출합니다.
- `static/data.csv`를 저장하면 다음 API 요청부터 변경 내용이 반영됩니다. 서버 재시작은 필요하지 않습니다.
- 서버 종료: `Ctrl+C`

## 데이터 형식

`static/data.csv`에는 다음 열이 필요합니다.

| 열 | 설명 | 예시 |
| --- | --- | --- |
| `name` | 장비명 | `서버-0001` |
| `status` | 장비 상태 | `정상`, `주의`, `점검필요` |
| `checked_at` | 점검 시각 | `2026-01-01T09:00:00+09:00` |
| `cpu` | CPU 사용률(%) | `12` |
| `mem` | 메모리 사용률(%) | `18` |

## 읽기 성능 비교

다음 명령으로 같은 데이터(각 1,000행)를 다섯 번씩 읽고 결과를 누적 기록합니다.

```powershell
py compare_reads.py
```

비교 대상은 다음 네 방식입니다.

| 파일 | 방식 |
| --- | --- |
| CSV | `csv.DictReader` |
| JSON | `json.loads` |
| CSV | `pandas.read_csv` |
| JSON | `pandas.read_json` |

실행 결과는 `logs/resource_log.csv`에 추가됩니다. 주요 열은 `elapsed_s`(실행 시간), `mem_delta_mb`(메모리 변화량), `cpu_pct`(CPU 사용률), `row_count`, `file_size_bytes`입니다.

## 참고

이 서버는 로컬 개발·실습용입니다. 외부에 공개하는 서비스로 사용하려면 인증, 입력 검증, 오류 로깅, 운영용 웹 서버 등을 별도로 갖춰야 합니다.
