# Shop 상품 목록과 상세 조회

Shop은 MySQL에 저장된 상품을 조회하고 상품명으로 검색하는 서버 렌더링 웹 애플리케이션이다. 목록의 상품명을 클릭하면 상품 번호·이름·가격을 표시하는 상세 화면으로 이동한다. 이 README는 실행 방법과 최종 폴더 구조, 기능명세, 검증 및 오류 처리 기준을 담는다.

작성일: 2026년 10월 7일 / 수정일: 2026년 10월 8일

## 기능 범위

| 기능 | 동작 |
| --- | --- |
| 상품 목록 | MySQL `products` 테이블에서 상품을 조회하여 ID 오름차순으로 표시 |
| 상품 상세 | 목록의 상품명을 클릭하여 해당 ID의 상품 번호·이름·가격을 확인. 목록 복귀 링크 제공 |
| 상품명 검색 | 검색어의 앞뒤 공백과 영문 대소문자를 무시하고 상품명 부분 일치 검색 |
| 결과 건수 | 현재 화면에 표시되는 상품 수를 `총 N개 상품`으로 표시 |
| 가격 표시 | 천 단위 구분 기호와 `원` 표시. 소수 가격은 정밀도를 유지 |
| 결과 없음 | 상품이 없거나 검색에 일치하는 상품이 없으면 `검색 결과가 없습니다.` 표시 |
| 정적 파일 | `/static/css/style.css`로 목록·상세 화면의 공통 스타일 제공 |
| 상품 등록 | `/product`에서 등록 폼 표시. 검증된 입력을 저장하고 등록 폼으로 303 리다이렉트 |

상품 수정·삭제, 주문, 재고 관리, 인증, 페이지네이션은 현재 구현 범위에 포함하지 않는다. 상품 조회용 JSON API도 제공하지 않는다.

## URL과 입력

| 메서드 | URL | 입력 | 성공 응답 |
| --- | --- | --- | --- |
| GET | `/` | 선택적 문자열 쿼리 `q`, 기본값 빈 문자열, 최대 200자 | 200, HTML 상품 목록 |
| GET | `/products/{product_id}` | 0보다 큰 정수 상품 ID | 200, HTML 상품 상세 |
| GET | `/product` | 없음 | 200, HTML 상품 등록 폼 |
| POST | `/product` | 폼의 `name`, `price`, `description`, `manager_code` | 303, `/product`로 리다이렉트 |
| GET | `/static/css/style.css` | 없음 | 200, CSS |

FastAPI의 기본 API 문서는 `/docs`와 `/redoc`, OpenAPI 정의는 `/openapi.json`에서 제공된다.

검색 입력은 HTML에서 최대 200자로 제한하고 서버에서도 같은 제한을 검증한다. 제한은 공백 제거 전 원래 입력 길이에 적용한다. 검색창에는 사용자가 입력한 원문을 유지한다.

## 검색 처리

1. 서비스가 검색어에 `strip().lower()`를 적용한다.
2. 저장소가 정규화한 검색어를 SQL 매개변수로 전달한다.
3. 검색어가 비어 있으면 전체 목록을 반환한다.
4. ASCII·한글 음절로 이루어진 검색어는 MySQL의 `LOWER(name)`과 바이너리 부분 검색으로 후보를 줄인다. 그 외 문자가 포함되면 전체 후보를 조회한다. 서비스가 Python의 `lower()`와 부분 일치로 최종 판정하여 기존 Unicode 검색 규칙을 유지한다.
5. 라우터가 결과와 원래 검색어를 `products/list.html`에 전달한다.

`/?q=노트`는 `노트북`에 일치한다. `/?q=%20MOUSE%20`는 `USB Mouse`에 일치한다. 검색어 중간의 공백은 제거하지 않으며, 정규식 검색이나 SQL 와일드카드 검색은 지원하지 않는다. 검색 결과는 원래 상품 정렬 순서를 유지한다.

일반적인 영문·한글 검색에서는 후보만 앱으로 가져와 전송량과 모델 생성을 줄인다. `LOCATE`를 사용해 `%`와 `_`도 문자 그대로 검색한다. MySQL과 Python의 Unicode 소문자 변환이 다른 경우를 처리하기 위해 서비스에서 최종 필터링한다. 전체 목록과 그 외 문자 검색은 전체 상품 수에 비례해 메모리를 사용하므로, 상품 수가 증가하면 페이지네이션을 검토한다. [MySQL 문자열 검색 문서](https://dev.mysql.com/doc/refman/8.4/en/string-functions.html)

## 상세 조회 처리

1. 목록의 상품명 링크가 `/products/{product_id}`로 이동한다.
2. 라우터가 상품 ID를 양의 정수로 검증한다.
3. 서비스가 저장소의 `get_by_id()`를 호출한다.
4. 저장소가 매개변수 바인딩을 사용하여 해당 상품만 조회한다.
5. 상품이 있으면 `products/detail.html`로 상세 정보를 표시한다. 없으면 404 JSON 응답을 반환한다.

상세 화면에서 목록으로 돌아가면 전체 목록을 표시하며, 이전 검색어를 복원하지 않는다.

## 상품 데이터 계약

등록 입력은 `ProductCreate` 폼 모델로 검증한다. 문자열의 앞뒤 공백은 제거하며, 공백만 있는 값은 허용하지 않는다. 상품명은 최대 255자, 담당자 코드는 최대 20자, 가격은 현재 MySQL INT 범위인 0부터 2147483647까지의 정수다. 상세설명은 필수이며 MySQL TEXT 크기에 맞춰 UTF-8 기준 최대 65535바이트로 검증한다.

등록 저장소는 매개변수 바인딩으로 INSERT를 실행하고 성공하면 커밋한다. 실패하면 롤백을 시도하며 최초 오류를 보존하고 커서·연결을 종료한다. 담당자 코드가 존재하지 않아 외래키 제약을 위반하면 400을 반환하고, 필수값 누락·입력 형식·범위 오류는 422를 반환한다.

등록을 사용하려면 아래 수동 마이그레이션으로 설명·담당자 컬럼 및 담당자 테이블을 먼저 준비해야 한다. 앱이 자동으로 스키마를 변경하지 않는다.

```sql
INSERT INTO products (name, price, description, manager_code)
VALUES (%s, %s, %s, %s);
```

조회 SQL:

```sql
SELECT id, name, price FROM products ORDER BY id;

-- 검색: %s에는 소문자로 정규화한 검색어를 바인딩한다.
SELECT id, name, price FROM products
WHERE LOCATE(CAST(%s AS BINARY), CAST(LOWER(name) AS BINARY)) > 0
ORDER BY id;

-- 상세 조회: %s에는 별도 매개변수로 상품 ID를 바인딩한다.
SELECT id, name, price FROM products WHERE id = %s;
```

| 필드 | Python 타입 | 검증 규칙 |
| --- | --- | --- |
| `id` | `int` | 0보다 큰 정수. 문자열이나 bool을 ID로 허용하지 않음 |
| `name` | `str` | 빈 문자열, 공백만 있는 이름, NULL을 허용하지 않음 |
| `price` | `Decimal` | 0 이상인 유한한 금액. 음수, NaN, 무한대, NULL을 허용하지 않음 |

DB 조회 결과는 `Product` 모델로 검증한다. 상품명은 검증 후 원문을 유지한다. 가격은 Decimal로 변환해 금액 계산과 표시에서 이진 부동소수점 오차를 피한다. 상품 모델은 생성 후 필드 변경을 허용하지 않는다.

MySQL 테이블과 컬럼은 사전에 준비되어 있어야 한다. 앱은 테이블을 생성하거나 데이터를 자동 적재하지 않는다. 상품 데이터 원본은 MySQL이며 JSON 파일을 사용하지 않는다. `id`는 기본키 또는 고유키로 관리한다.

## 오류 처리

| 상황 | 결과 |
| --- | --- |
| 필수 설정 누락 또는 잘못된 설정 | 앱 시작 실패. Pydantic 설정 검증 오류 발생 |
| 검색어 200자 초과 | 422, FastAPI 검증 오류 JSON |
| 상품 등록 입력 누락·공백·길이·가격 범위 오류 | 422, FastAPI 검증 오류 JSON |
| 등록되지 않은 담당자 코드로 등록 | 400, `{"detail":"등록되지 않은 담당자 코드입니다."}` |
| 상품 ID가 정수가 아니거나 0 이하 | 422, FastAPI 검증 오류 JSON |
| 해당 ID의 상품 없음 | 404, `{"detail":"상품을 찾을 수 없습니다."}` |
| DB 연결·쿼리·커서 정리에서 MySQL 오류 발생 | 503, `{"detail":"상품을 불러올 수 없습니다. 잠시 후 다시 시도해 주세요."}` |
| 저장된 상품 데이터 검증 실패 | 500, `{"detail":"상품 데이터가 올바르지 않습니다."}` |
| 검색 결과 없음 | 200, HTML 빈 결과 안내 |
| 존재하지 않는 URL | 404 |

DB 장애와 잘못된 상품 데이터에 대한 응답은 JSON이다. 연결 정보, SQL 오류 원문, 검증에 실패한 상품 원문은 해당 HTTP 응답에 노출하지 않는다. 연결을 성공적으로 생성한 경우 작업 실패나 커서 생성 실패 시에도 연결 종료를 시도하며, 생성된 커서는 조회 성공과 실패 모두에서 종료를 시도한다.

템플릿은 Jinja2의 HTML 이스케이프를 사용한다. 상품명과 검색어를 HTML 태그로 실행하지 않고 텍스트로 표시한다. MySQL 작업은 동기 방식이며, 목록과 상세 라우터도 동기 함수로 실행한다.

## 모듈 구조

```text
shop/
├─ app/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ config.py
│  ├─ database.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ product.py
│  ├─ repositories/
│  │  ├─ __init__.py
│  │  └─ product.py
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ product.py
│  └─ routers/
│     ├─ __init__.py
│     └─ product.py
├─ templates/
│  ├─ base.html
│  ├─ product.html
│  └─ products/
│     ├─ list.html
│     └─ detail.html
├─ static/
│  └─ css/
│     └─ style.css
├─ tests/
│  ├─ __init__.py
│  ├─ helpers.py
│  ├─ test_connection.py
│  ├─ test_config.py
│  ├─ test_migration.py
│  ├─ test_product_service.py
│  ├─ test_repository.py
│  ├─ test_registration.py
│  └─ test_routes.py
├─ .env.example
├─ migrate_shop_db.py
├─ requirements.txt
├─ requirements-dev.txt
└─ README.md
```

| 모듈 | 책임 |
| --- | --- |
| `app/main.py` | 앱 생성, 시작 시 설정 검증, 라우터·정적 파일·오류 처리 등록 |
| `app/config.py` | 환경변수 로딩과 검증, shop 기준 경로, 설정 캐시 |
| `app/database.py` | MySQL 연결·커서의 공통 수명 관리 |
| `app/models/product.py` | 상품 타입 및 저장된 데이터 검증 |
| `app/repositories/product.py` | SQL 실행, 상품 모델 변환, 저장소 오류 분류 |
| `app/services/product.py` | 화면·HTTP에 독립적인 상품 검색·상세 조회·등록 로직 |
| `app/routers/product.py` | 쿼리와 상품 ID 검증, 서비스 주입, 목록·상세 템플릿 응답 |
| `templates/products/` | 상품 목록·상세 화면 |
| `static/css/style.css` | 목록·상세 화면의 공통 스타일 |
| `templates/base.html` | 페이지 공통 HTML 구조와 CSS 연결 |
| `templates/product.html` | GET `/product` 등록 화면과 POST `/product` 입력 폼 |
| `migrate_shop_db.py` | 수동 실행하는 설명·담당자 스키마 마이그레이션 |

서비스는 `ProductStore` Protocol을 사용한다. `list_products(keyword: str = "") -> list[Product]`, `get_by_id(product_id: int) -> Product | None`, `save_product(product: ProductCreate) -> None` 계약을 구현한 다른 저장소로 교체할 수 있다. `create_app(settings)`와 FastAPI 의존성 교체를 통해 테스트에서 설정과 서비스를 주입할 수 있다.

## 환경설정

프로세스 환경변수가 우선이며, 누락된 값은 `shop/.env`에서 읽는다. `.env`는 Git에서 제외한다. 설정은 프로세스 내에서 캐시하므로 설정 변경 후 앱을 다시 시작한다.

| 환경변수 | 필수 | 기본값과 검증 |
| --- | --- | --- |
| `MYSQL_HOST` | 예 | 앞뒤 공백 제거 후 비어 있지 않은 문자열 |
| `MYSQL_PORT` | 아니요 | 3306, 1부터 65535까지의 정수 |
| `MYSQL_USER` | 예 | 앞뒤 공백 제거 후 비어 있지 않은 문자열 |
| `MYSQL_PASSWORD` | 예 | 공백만 있는 값 불가. 비밀번호 자체의 앞뒤 공백은 유지 |
| `MYSQL_DATABASE` | 예 | 앞뒤 공백 제거 후 비어 있지 않은 문자열 |
| `MYSQL_CONNECTION_TIMEOUT` | 아니요 | 5초, 1부터 60까지의 정수. DB 연결 수립 시간 제한 |

비밀번호는 SecretStr로 저장하여 설정 객체의 문자열 표현에서 숨긴다. 설정 검증 오류의 일반 문자열 표현에도 입력값을 표시하지 않는다.

## 설치와 실행

검증 환경은 Python 3.12다. 아래 명령은 `shop` 디렉터리에서 실행한다.

```powershell
python -m pip install -r requirements.txt
```

새 환경에서는 `.env.example`을 `.env`로 복사하고 실제 접속 정보로 수정한다. 이미 `.env`가 있다면 기존 파일을 사용한다.

```powershell
Copy-Item .env.example .env
```

앱을 실행한다.

```powershell
python -m uvicorn app.main:app --reload
```

IDE에서 `app/main.py` 파일을 직접 실행해도 서버가 시작된다. 직접 실행은 자동 재시작을 사용하지 않으며, 개발 중 자동 재시작이 필요하면 위 Uvicorn 명령을 사용한다.

```powershell
python app/main.py
```

기본 주소는 `http://127.0.0.1:8000/`이다. 시작점은 `app/main.py`이며, 다른 작업 디렉터리에서는 `--app-dir`에 shop의 경로를 지정한다. `.env`는 로컬 설정 파일이므로 위 공유 폴더 구조에서 생략했다. 서버 로그에는 저장소 오류의 타입·MySQL 오류 번호·SQLSTATE를 기록하며, 비밀번호나 SQL 오류 원문을 기록하지 않는다.

## 수동 DB 마이그레이션

```powershell
python migrate_shop_db.py
```

접속 대상은 앱과 동일한 `.env` 설정이다. 마이그레이션은 앱 시작과 별도로 수동 실행하며, 계정에는 테이블 생성·변경 및 데이터 수정 권한이 필요하다.

마이그레이션은 다음을 수행한다.

- `products` 테이블이 준비되어 있는지 확인하고 기존 설명·담당자 컬럼과 외래키의 정의를 검증한다.
- 필요한 경우에만 InnoDB 전환, 담당자 테이블 생성, 설명·담당자 컬럼 추가 및 NOT NULL 변경을 수행한다.
- 담당자 A/B/C를 저장한다. 같은 코드가 이미 있으면 이름·전화번호를 샘플 값으로 갱신한다.
- 설명 NULL은 빈 문자열, 담당자 NULL은 A로 채운다. 이미 지정된 값은 유지한다.
- 등록되지 않은 담당자 코드가 있으면 외래키 추가를 중단한다.
- 외래키가 없을 때만 추가한다. 이미 존재하는 외래키는 컬럼·참조 대상·CASCADE/RESTRICT 규칙까지 확인한다.

완료된 스키마에 재실행하면 불필요한 ALTER TABLE과 NULL 보정 UPDATE를 건너뛴다. `manager_code`의 문자셋과 콜레이션은 참조 대상과 일치하도록 설정한다. MySQL DDL은 암묵적 커밋을 발생시키므로 실패해도 이전 구조 변경이 남을 수 있다. [MySQL 트랜잭션 문서](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html)

## 테스트

표준 라이브러리 unittest를 사용한다. 실행 의존성은 `requirements.txt`, HTTP 테스트 의존성은 `requirements-dev.txt`로 분리한다.

```powershell
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

기본 실행은 실제 DB를 사용하지 않는다. 설정 검증과 dotenv 우선순위, 상품 데이터 검증, Unicode와 SQL 검색 규칙, 커서와 연결 정리, 목록·상세 HTML과 이스케이프, 등록 화면·입력 검증·303 리다이렉트·커밋·롤백·외래키 오류, 오류 응답·로그, 앱 시작 검증을 확인한다. 마이그레이션은 모의 연결로 최초 실행·재실행·잘못된 스키마·외래키·담당자 코드·자원 정리를 검증한다. 실제 MySQL 연결 및 상품 조회 테스트 2개는 기본적으로 건너뛴다. 등록 테스트는 모의 저장소와 연결을 사용하므로 실제 상품을 추가하지 않는다.

실제 DB 테스트는 설정된 MySQL에서 `SELECT 1`과 상품 조회만 실행한다.

```powershell
$env:RUN_MYSQL_INTEGRATION_TESTS = "1"
python -m unittest tests.test_connection.MySQLIntegrationTests -v
Remove-Item Env:RUN_MYSQL_INTEGRATION_TESTS
```

통합 테스트가 성공하려면 MySQL이 해당 호스트와 포트에서 접속을 허용하고, 계정에 상품 테이블 SELECT 권한이 있어야 한다.
