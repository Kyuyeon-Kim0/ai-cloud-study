# MySQL 재고 관리 프로젝트

학습 날짜: 2026-10-08 (목)

FastAPI와 MySQL로 상품과 입출고를 관리하는 로컬 웹 애플리케이션입니다. 상품 조회만 제공하던 초기 코드를 확장하여 상품 관리, 재고 변동 이력, 검색과 현황 요약을 제공합니다.

## 주요 기능

- 상품 등록·조회·수정·삭제와 상품명 검색, 페이지 조회
- 초기 재고 등록, 입고·출고와 사유 기록
- 안전 재고 이하 상품 조회, 상품 수·전체 수량·재고 금액 요약
- 웹 대시보드와 Swagger API 문서
- 삭제된 상품의 입출고 이력 보존
- MySQL 트랜잭션과 `SELECT ... FOR UPDATE`를 이용한 동시 출고 보호
- 음수 재고, 잘못된 금액·수량·상품명 검증

가격은 원 단위이며 소수 둘째 자리까지 저장합니다. 재고는 정수이고, 안전 재고 이하이면 재고 부족으로 표시합니다. 상품 수정으로 수량을 바꾸지 않고 입출고 API를 통해 수량과 이력을 함께 갱신합니다. 초기 재고가 0보다 크면 최초 입고 이력이 기록됩니다.

재고가 남은 상품은 삭제할 수 없습니다. 출고로 재고를 0으로 만든 뒤 삭제하면 목록에서 제외되며 DB와 이력은 보존됩니다. 상품명 수정 시 과거 이력 화면에도 현재 상품명이 표시됩니다.

## 준비 사항

- Python 3.12와 Windows PowerShell
- 실행 중인 MySQL 8.x와 사용 가능한 데이터베이스
- 테이블 생성·변경 및 데이터 조회·수정 권한을 가진 계정
- 자동 통합 테스트에는 Docker Desktop 필요

인증 기능이 없는 개인 학습용 앱입니다. 기본 실행은 로컬 주소에 바인딩합니다.

## 설치 및 실행

```powershell
cd C:\ai-starter\2026-10\10-08\inventory_project
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

기존 `.env`가 있으면 그대로 사용합니다. 새로 설치할 때만 예시를 복사하고 실제 DB 연결 정보를 설정합니다.

```powershell
Copy-Item .env.example .env
```

환경 변수 목록:

| 변수 | 내용 |
| --- | --- |
| `APP_NAME`, `APP_ENV` | 앱 이름과 실행 환경 |
| `MYSQL_HOST`, `MYSQL_PORT` | MySQL 주소와 포트 (예시: `127.0.0.1:3307`) |
| `MYSQL_USER`, `MYSQL_PASSWORD` | DB 계정과 비밀번호 |
| `MYSQL_DATABASE` | 사용할 DB 이름 |

`.env`는 프로젝트 폴더의 파일을 절대 경로로 읽으며, 동일 이름의 실행 환경 변수가 우선합니다. 실제 비밀번호는 Git에 올리지 않습니다.

DB 연결을 확인하고 테이블을 초기화한 뒤 서버를 실행합니다.

```powershell
python test.py
python init_db.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

- 웹 화면: <http://127.0.0.1:8010/dashboard>
- API 문서: <http://127.0.0.1:8010/docs>
- DB 연결 확인: <http://127.0.0.1:8010/health>
- 종료: 터미널에서 `Ctrl+C`

`init_db.py`는 기존 상품을 삭제하지 않습니다. 초기 `products` 테이블에 재고·안전 재고·삭제 시각 열을 추가하고, 정수 가격 열을 `DECIMAL(12,2)`로 확장하며, 입출고 테이블을 만듭니다. 기존 상품의 초기 재고는 0으로 설정되므로 실제 보유량을 입고 처리하세요. MySQL DDL은 자동 커밋되므로 중요한 데이터가 있는 DB에서는 스키마 변경 전 백업을 준비합니다.

## 사용 방법

1. 대시보드의 **상품 등록**에서 이름·가격·초기 재고·안전 재고를 입력합니다.
2. 상품의 **입출고**에서 처리 방향, 수량, 사유를 입력합니다.
3. 검색과 **재고 부족만** 필터로 상품을 찾습니다.
4. **이력**으로 상품별 입출고를 보고, **전체 이력**으로 최근 100건을 확인합니다.
5. **수정**에서 이름·가격·안전 재고를 바꿉니다. **삭제**는 재고가 0일 때 가능합니다.

화면은 상품을 페이지당 20개씩 표시합니다. 상단 요약은 검색 조건과 관계없이 전체 활성 상품을 기준으로 계산합니다.

## API

| 메서드 | 경로 | 기능 |
| --- | --- | --- |
| GET | `/` | 앱 정보 |
| GET | `/health` | DB 연결 확인 |
| GET | `/api/products` | 목록 (`q`, `low_stock`, `limit`, `offset`) |
| POST | `/api/products` | 상품 등록 |
| GET | `/api/products/{id}` | 상품 상세 |
| PUT | `/api/products/{id}` | 이름·가격·안전 재고 전체 수정 |
| DELETE | `/api/products/{id}` | 재고가 0인 상품을 목록에서 제외 |
| POST | `/api/products/{id}/stock` | 입출고 |
| GET | `/api/movements` | 이력 (`product_id`, `limit`, `offset`) |
| GET | `/api/summary` | 전체 현황 요약 |

목록과 이력은 `limit` 1~100, `offset` 0 이상을 받습니다. 금액은 정밀도 보존을 위해 JSON에서 문자열로 반환합니다. 수량 입력은 문자열·소수·불리언을 허용하지 않습니다.

상품 등록 예시:

```json
{
  "product_name": "무선 마우스",
  "price": "25000.00",
  "quantity": 10,
  "min_stock": 3
}
```

입출고 예시 (`direction`은 `in` 또는 `out`):

```json
{
  "direction": "out",
  "quantity": 2,
  "reason": "판매 출고"
}
```

입력 오류는 422, 상품 없음은 404, 재고 부족·삭제 불가·수량 범위 초과는 409, DB 연결·처리 실패는 503을 반환합니다. DB 오류 응답에는 접속 비밀번호나 내부 SQL 내용을 넣지 않습니다.

## MySQL 새로 준비하기 (선택)

기존 MySQL 서버가 있으면 이 단계는 필요 없습니다. 새 환경에서는 `.env`의 DB 계정·이름·포트를 설정하고 Docker Desktop을 실행한 뒤 다음처럼 준비할 수 있습니다. `MYSQL_USER`에는 `root`가 아닌 앱 계정을 사용합니다.

```powershell
$env:MYSQL_ROOT_PASSWORD = "replace-with-a-strong-root-password"
docker compose up -d --wait
python init_db.py
```

DB 데이터는 Compose의 `mysql_data` 볼륨에 저장됩니다. `docker compose down`은 컨테이너를 종료하고 데이터를 유지합니다. `down -v`는 데이터를 삭제하므로 사용하지 않습니다. 이미 사용 중인 포트라면 기존 서버를 사용하거나 `.env`의 포트를 바꿉니다. 볼륨 생성 후 비밀번호 변경은 MySQL 내에서 별도 처리해야 합니다.

## 테스트

```powershell
python -m pip install -r requirements-dev.txt
python run_tests.py
```

`run_tests.py`는 MySQL 8.4 임시 컨테이너를 임의의 로컬 포트에 만들고, `inventory_test` DB에서 테스트한 뒤 컨테이너를 삭제합니다. 기존 `.env`의 데이터베이스에는 테스트 데이터를 쓰지 않습니다. 첫 실행에는 이미지 다운로드가 필요할 수 있습니다. 직접 `pytest`를 실행하면 안전을 위해 통합 테스트가 건너뛰어집니다.

검증 항목: 상품 관리, 금액 정밀도, 입출고와 이력, 검색·페이지·재고 부족 조회, 입력 검증, 동시 출고, 이력 기록 실패 시 롤백, DB 오류 응답, 초기화 반복 실행, 기존 스키마 마이그레이션.

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `app/main.py` | 앱, 웹 파일 제공, 상태 확인과 DB 오류 처리 |
| `app/config.py`, `app/database.py` | 환경 변수와 MySQL 연결 |
| `app/schemas.py` | 상품·입출고 입력과 출력 모델 |
| `app/routers/products.py` | API 라우트 |
| `app/services/product_service.py` | 트랜잭션 기반 상품·재고 처리 |
| `app/static/` | HTML·CSS·JavaScript 웹 화면 |
| `init_db.py` | 테이블 생성과 기존 스키마 보완 |
| `test.py` | 기존 MySQL 연결 점검 |
| `run_tests.py`, `tests/` | 임시 MySQL 통합 테스트 |
| `compose.yaml` | 선택적으로 새 MySQL 서버 실행 |
| `.env.example` | 공유 가능한 환경 변수 예시 |

## 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| DB 연결 실패·503 | MySQL 실행 여부, `.env` 주소·포트·계정·DB 이름 확인 |
| 테이블 또는 재고 열 없음 | `python init_db.py` 실행 및 DDL 권한 확인 |
| Docker 포트 충돌 | 이미 실행 중인 MySQL 사용 또는 포트 변경 |
| 출고·삭제 요청 409 | 현재 재고 수량과 출고 수량 확인 |
| 화면에서 상품이 보이지 않음 | 검색·재고 부족 필터 해제, 페이지와 오류 메시지 확인 |
| 테스트가 건너뛰어짐 | Docker Desktop을 실행하고 `python run_tests.py` 사용 |
