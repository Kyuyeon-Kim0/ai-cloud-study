# 2026-09-15 (화) 학습 기록

## 학습 주제

- 정적 웹과 동적 웹의 차이
- 사용자 행동 및 시스템 자원 사용량 기록
- CSV·JSON 데이터 읽기 방식과 성능 비교
- 대용량 데이터 처리, 외부 API 캐시, SQLite, 대시보드

## 핵심 이해

### 웹 서비스와 시스템 자원

- 웹 서비스의 실행과 사용자 활동은 접속·클릭 등의 로그로 기록할 수 있습니다.
- CPU, 메모리, 네트워크 사용량을 함께 측정하면 사용자 활동과 시스템 상태의 관계를 관찰할 수 있습니다.

### 데이터 처리 방식

- 같은 데이터라도 CSV, JSON, 표준 라이브러리, `pandas`, SQLite 등 처리 방법에 따라 성능과 자원 사용량이 달라질 수 있습니다.
- 측정 결과는 PC 사양, 파일 캐시, 실행 시점의 부하에 따라 달라질 수 있습니다.

## 실습 내용

- 브라우저 클릭 게임과 사용자 행동 로그 기록
- 장비 점검 현황 API 및 CSV·JSON 읽기 성능 비교
- 가상 포켓몬 데이터 생성, 집계, PokeAPI 캐시, SQLite 적재 및 Streamlit 대시보드

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| `09.15_교안_정적,동적html이해_자료에따른 자원차이/` | 정적·동적 웹, 데이터 처리, API, 대시보드를 다루는 HTML 교안 |
| [html_game/](html_game/README.md) | 클릭 게임, 사용자 행동 로그, 시스템 자원 모니터링 실습 |
| [web-lab/](web-lab/README.md) | 장비 현황 웹 API와 CSV·JSON 읽기 성능 비교 실습 |
| [poke-lab/](poke-lab/README.md) | 대용량 포켓몬 데이터 처리, PokeAPI 캐시, SQLite, Streamlit 대시보드 실습 |
| `memo.txt` | SQLite 변환 실습 및 후속 질문 메모 |

## 실행 방법

각 실습은 해당 하위 프로젝트 폴더에서 실행합니다. 설치, 실행 명령, 접속 주소와 문제 해결 방법은 각 프로젝트 README를 따릅니다.

```powershell
cd C:\ai-starter\2026-09\09-15
```

- HTML 게임: [html_game 실행 안내](html_game/README.md)
- 장비 현황 API: [web-lab 실행 안내](web-lab/README.md)
- 포켓몬 데이터 처리: [poke-lab 실행 안내](poke-lab/README.md)
