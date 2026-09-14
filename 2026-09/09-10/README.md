# 2026-09-10 (목) 학습 기록

## 강의 자료

- `09.10_시스템엔지니어_MSP_클라우드_교안.html`
- `09.10_공공데이터_API_발급.pdf`

## 강의 시간

- 1교시: 1일차 학습 내용 정리, GPT 및 Codex 사용법
- 2교시~점심 전: 네트워크와 URL의 이해
- 3교시(13:00~14:20): 공개 API 자료 받기, JSON과 XML 등 데이터 파일 이해
- 4교시(15:00~16:20): 오전 학습 및 실습 내용 정리
- 5교시(16:30~18:00): Python을 활용한 공공데이터 API 연결 실습 및 API 인증 방법 학습

## 핵심 이해

### 네트워크와 URL

- 네트워크는 서로 다른 장치가 데이터를 주고받는 구조이다.
- URL은 인터넷 자원의 위치와 접근 방법을 표현한다.
- URL의 구성 요소를 이해하면 외부 API의 주소와 요청 방식을 파악할 수 있다.
- 네트워크 자체에 대한 별도 강의는 9월 18일부터 진행할 예정이다.

### 공개 API와 데이터 형식

- 공개 API를 통해 외부 서비스에서 제공하는 데이터를 요청하고 받을 수 있다.
- JSON은 키와 값으로 구성된 구조화된 데이터 형식으로, API 응답에 자주 사용된다.
- XML은 태그를 이용해 데이터를 표현하는 형식이며, JSON과 함께 API 데이터 교환에 사용된다.
- API를 사용하려면 서비스별 인증 방법과 발급받은 API 키를 확인해야 한다.

### GPT, Codex와 바이브코딩

- 자연어로 요구 사항을 설명하며 API 연결 코드를 작성하고 수정할 수 있다.
- GPT와 Codex를 활용할 때는 API 주소, 인증 방식, 요청 조건, 응답 데이터 형식을 구체적으로 전달하는 것이 중요하다.
- 실행 결과를 확인하고 오류를 수정하는 과정을 반복하며 API 사용 흐름을 익혔다.

### 환율 API와 CSV 활용

- Frankfurter API에서 USD 기준 KRW·JPY·EUR 환율을 받아 CSV 파일로 저장한다.
- HTML·JavaScript 계산기가 CSV를 읽어 USD·KRW·JPY·EUR 사이의 금액을 환산한다.
- API에서 데이터를 수집하는 단계와 저장된 CSV를 읽어 사용하는 단계를 구분한다.
- 화면의 `CSV 다시 읽기`는 저장된 파일을 다시 읽으며, API 환율 갱신은 `update-rates.ps1`로 실행한다.

## 실습 내용

- URL 구성을 분석하여 외부 API 요청의 기본 구조 확인
- 공개 API 자료 요청 및 응답 데이터 확인
- JSON과 XML 데이터 형식 비교
- 공공데이터 API 인증 방법 확인
- Python 기반 공공데이터 API 연결 실습
- 환율 API 응답을 CSV로 저장하고 웹 계산기에서 통화 간 환산

## 실습 파일

| 파일 또는 폴더 | 내용 |
|---|---|
| [restart_wifi.ps1](restart_wifi.ps1) | Wi-Fi 재시작 및 네트워크 연결 확인 |
| [exchange-calculator/](exchange-calculator/README.md) | API 환율 수집, CSV 저장, 웹 기반 환율 계산 |
| [tago-train-api/](tago-train-api/README.md) | 공공데이터 기차 시간표 조회 및 서비스 점검 에이전트 |

## 환율 계산기 실행

PowerShell에서 이동한 프로젝트 폴더를 기준으로 실행한다.

```powershell
cd C:\ai-starter\2026-09\09-10\exchange-calculator
.\start.cmd
```

환율 데이터를 갱신하려면 같은 폴더에서 다음 명령을 실행한 뒤 화면의 `CSV 다시 읽기`를 누른다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\update-rates.ps1
```
