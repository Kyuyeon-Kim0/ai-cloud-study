환율 계산기

1. start.cmd를 더블클릭하면 브라우저가 열리고 저장된 CSV를 자동으로 읽습니다.
   실행 창을 닫으면 로컬 서버가 종료됩니다.
2. index.html을 직접 열어도 됩니다. 이 경우 화면에서 data\exchange-rates.csv를 선택하세요.
3. 최신 환율을 다시 저장하려면 PowerShell에서 실행하세요.
   cd C:\ai-starter\exchange-calculator
   powershell -NoProfile -ExecutionPolicy Bypass -File .\update-rates.ps1
   이후 계산기의 'CSV 다시 읽기'를 누르세요.

CSV: data\exchange-rates.csv
수집 코드: update-rates.ps1
화면: index.html
CSV 파싱 및 계산 코드: calculator.js

계산식: 입력 금액 / 보내는 통화의 USD 기준 환율 * 받는 통화의 USD 기준 환율
내부 계산에는 원본 정밀도를 사용하고 화면의 결과만 소수 둘째 자리까지 표시합니다.
CSV의 date는 API가 제공한 환율 기준일이며 fetched_at_utc는 수집 시각입니다.
source 열에는 원본 API 주소가 저장됩니다. 갱신에 실패하면 기존 CSV를 유지합니다.
이 계산기는 저장된 CSV만 읽으며 화면에서 API를 직접 호출하지 않습니다.
