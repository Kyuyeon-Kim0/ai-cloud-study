# CSV 환율 계산기 · Codex 작업 인계

작성일: 2026-09-10

## 다음 Codex 작업에서 시작하기

아래 내용을 새 작업에 붙여 넣으세요.

> C:\ai-starter\exchange-calculator\README.md를 먼저 읽고 기존 환율 계산기 작업을 이어서 진행해줘. 프로젝트 폴더는 C:\ai-starter\exchange-calculator야. 기존 파일과 현재 동작을 확인한 후 내가 요청한 변경을 적용해줘.

원하는 변경 사항을 이 문장 뒤에 추가하면 됩니다. 새 작업에서는 이 README와 실제 파일을 기준으로 상태를 확인하세요. 이전 대화나 로컬 서버가 유지된다고 가정하지 마세요.

## 목적과 현재 상태

사용자가 지정한 Frankfurter API에서 USD 기준 KRW·JPY·EUR 환율을 수집해 로컬 CSV에 저장하고, HTML 계산기가 그 CSV를 읽어 네 통화 사이의 환산을 수행합니다.

- 프로젝트: `C:\ai-starter\exchange-calculator`
- 별도 프레임워크나 npm 설치 없이 HTML/CSS/JavaScript로 구현했습니다.
- 외부 호스팅 없이 로컬에서 실행합니다.
- API 수집과 CSV 저장, 계산기 구현은 완료했습니다.
- 이번 요청은 다음 작업을 위한 문서 작성입니다. 버튼의 갱신 동작 변경은 아직 요청되거나 구현되지 않았습니다.

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `index.html` | 한국어 화면, 입력·통화 선택·통화 교환, 파일 선택, CSV 다시 읽기 |
| `calculator.js` | CSV 파싱·검증과 환산 함수. 브라우저 및 Node.js에서 사용 가능 |
| `data/exchange-rates.csv` | 실제 환율 자료와 출처, 기준일, 수집 시각 |
| `update-rates.ps1` | API를 호출하고 검증한 뒤 CSV를 교체하는 수집 코드 |
| `serve.py` | 프로젝트 폴더만 제공하는 Python 로컬 HTTP 서버 |
| `start.ps1` | Python 실행 파일을 찾아 서버 실행 |
| `start.cmd` | 더블클릭 실행용 진입점 |
| `.preview-url` | 서버 시작 시 기록되는 로컬 주소. 다음 실행 때 달라질 수 있음 |
| `README.txt` | 최초 작성한 간단한 사용 안내 |
| `README.md` | 현재 작업 인계 문서 |

## 실행 방법

Windows에서 `start.cmd`를 더블클릭하거나 PowerShell에서 실행합니다.

```powershell
cd C:\ai-starter\exchange-calculator
.\start.cmd
```

Python 3가 필요합니다. `start.ps1`은 현재 사용자 폴더의 Codex 번들 Python을 우선 사용하고, 없으면 PATH의 `python`을 찾습니다. 다른 PC에서 실행할 경우 Python 설치 여부를 확인하세요.

서버는 `127.0.0.1`의 사용 가능한 포트에만 연결하며 브라우저를 엽니다. 실행 창을 닫거나 Ctrl+C로 종료할 수 있습니다. 실행할 때마다 포트가 달라질 수 있으므로 예전 주소를 고정해서 사용하지 마세요.

`index.html`을 직접 열 수도 있습니다. 이 경우 브라우저의 로컬 파일 제한 때문에 자동 읽기 대신 화면에서 `data/exchange-rates.csv`를 선택해야 합니다.

## 환율 갱신 방법과 버튼의 정확한 의미

```powershell
cd C:\ai-starter\exchange-calculator
powershell -NoProfile -ExecutionPolicy Bypass -File .\update-rates.ps1
```

실행 성공 후 계산기의 **CSV 다시 읽기** 버튼을 누르세요. 파일을 직접 연 모드에서는 갱신한 CSV를 다시 선택하세요.

**현재 버튼은 디스크에 저장된 CSV만 읽습니다. API를 호출하거나 CSV를 새로 저장하지 않습니다.** 자동 갱신, 주기적 수집, 실시간 환율 조회도 구현하지 않았습니다.

- `date`: API가 제공한 환율 기준일. 화면 상단에 표시합니다.
- `fetched_at_utc`: API를 수집한 UTC 시각. CSV에 저장하지만 현재 화면에는 표시하지 않습니다.
- API 수집에 성공하면 수집 시각은 새로 기록됩니다. 제공 자료가 같으면 기준일과 환율은 그대로일 수 있습니다.
- 갱신 코드가 실패하면 기존 CSV를 유지하도록 임시 파일 작성 후 교체합니다.

사용자는 이전에 “CSV 다시 읽기를 누르면 시간과 환율이 갱신되는가?”라고 질문했고, 위 동작을 설명받았습니다. 향후 버튼 변경 요청이 오면 이 차이를 먼저 확인하세요. 현재 Python 서버는 정적 파일 제공용이므로 버튼에서 수집하려면 별도의 서버 처리 구현이 필요합니다. 그런 변경 시 로컬 요청 검증과 실패 시 기존 CSV 보존도 고려하세요.

## 데이터 형식과 계산 방식

출처: <https://api.frankfurter.dev/v1/latest?from=USD&to=KRW,JPY,EUR>

CSV는 UTF-8이며 다음 열을 갖습니다. API 주소에 쉼표가 포함되므로 단순히 쉼표로 분리하지 말고 CSV 인용부호를 처리해야 합니다.

```text
date,base,currency,rate,fetched_at_utc,source
```

KRW·JPY·EUR 각 한 행을 저장하고 USD 환율은 계산 코드에서 1로 사용합니다. 모든 행의 기준일과 기준 통화가 같아야 하며, 중복 통화·누락 통화·0 이하 환율은 오류로 처리합니다.

```text
받는 금액 = 입력 금액 / 보내는 통화의 USD 기준 환율 × 받는 통화의 USD 기준 환율
```

내부 계산에는 CSV의 원본 숫자를 사용하고, 결과는 최대 소수 둘째 자리까지 표시합니다. 단위 환율은 최대 소수 여섯째 자리까지 표시합니다. 0은 허용하고 음수·빈 입력·유한하지 않은 값은 오류로 처리합니다. 은행별 환율이나 환전 수수료는 반영하지 않습니다.

문서 작성 시 저장된 자료는 아래와 같습니다. 향후에는 실제 CSV를 확인하세요.

| 기준일 | 기준 | 통화 | 환율 |
| --- | --- | --- | ---: |
| 2026-09-09 | USD | KRW | 1336.2 |
| 2026-09-09 | USD | JPY | 153.27 |
| 2026-09-09 | USD | EUR | 0.85822 |

수집 시각: `2026-09-10T05:33:53.8465090Z`

## 완료한 검증과 다음 수정 시 확인할 사항

초기 구현에서 실제 CSV 파싱, 100 USD → 133,620 KRW, 역환산, EUR → JPY 교차 환산, 0·음수 입력, 잘못된 CSV 처리를 검증했습니다. HTML 안의 JavaScript 구문과 로컬 HTTP 서버의 HTML·CSV 응답(200)도 확인했습니다. 브라우저 자동 클릭 및 시각 검사는 수행하지 않았습니다.

수정 후에는 실제 CSV를 다시 읽고 변경한 기능을 중심으로 확인하세요. 환율을 새로 수집했다면 위 예시 금액을 고정된 최신 환율로 가정하지 마세요.

Node.js가 PATH에 있다면 프로젝트 폴더에서 다음으로 핵심 동작을 확인할 수 있습니다.

```powershell
node -e "const fs=require('fs'),assert=require('assert/strict'),x=require('./calculator.js');const d=x.readRates(fs.readFileSync('./data/exchange-rates.csv','utf8'));const v=x.convert(100,'USD','KRW',d.rates);assert.ok(Math.abs(v-100*d.rates.KRW)<1e-8);assert.ok(Math.abs(x.convert(v,'KRW','USD',d.rates)-100)<1e-8);assert.equal(x.convert(0,'USD','JPY',d.rates),0);assert.throws(()=>x.convert(-1,'USD','KRW',d.rates));console.log('PASS',d.date);"
```

현재 PC에서 Node.js가 PATH에 없으면 다음 실행 파일을 사용할 수 있습니다.

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" --version
```

향후 기능을 수정하면 이 문서의 현재 동작, 실행 방법, 검증 내역도 함께 갱신하세요.
