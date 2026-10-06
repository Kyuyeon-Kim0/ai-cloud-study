# 2026-10-06 (화) 학습 기록

## 학습 주제

- Python 모듈을 역할별로 나누어 프로젝트 구조 잡기
- CSV 데이터 읽기, 매출 집계, JSON 반환값 설계
- 함수 시그니처와 타입 힌트로 도구 명세 만들기
- 데코레이터와 레지스트리를 이용한 함수 등록·호출
- 모듈 자동 로딩과 CLI 구성
- 클래스, 인스턴스, 메서드, 상속, `super()`, 오버라이딩 이해

## 핵심 이해

### 데이터 처리와 반환값 설계

- CSV에서 읽은 값은 문자열이므로 수량과 가격을 숫자로 변환한 뒤 매출액을 계산합니다.
- 데이터 읽기는 `loader.py`, 집계와 필터링은 `sales_tools.py`로 나누어 각 파일의 역할을 분리합니다.
- 결과는 딕셔너리와 리스트로 구성하고 `json.dumps()`로 JSON 문자열로 변환합니다.
- `datetime`, `Decimal`처럼 기본 JSON 인코더가 처리하지 못하는 값은 문자열이나 숫자 등으로 변환해야 합니다.
- 조회 결과가 없어도 `count`, `total`, `items` 같은 반환 구조를 유지하면 호출하는 쪽에서 일관되게 처리할 수 있습니다.

### 함수 명세와 도구 등록

- `inspect.signature()`로 매개변수와 기본값을 읽고, `get_type_hints()`로 타입 정보를 가져옵니다.
- 함수 이름, docstring, 타입 힌트를 조합해 도구 이름·설명·매개변수 명세를 만듭니다.
- 기본값이 없는 매개변수는 필수 인자로, 기본값이 있는 매개변수는 선택 인자로 표시합니다.
- `@tool` 데코레이터는 함수를 레지스트리에 등록하고, `functools.wraps()`는 감싼 함수의 이름과 docstring 등 정보를 보존합니다.
- `call_tool()`은 도구 이름으로 함수를 찾아 인자 딕셔너리를 `**arguments` 형태로 전달합니다.
- 현재 실습의 타입 힌트와 명세는 입력값의 타입을 자동으로 검사하지 않습니다.

### 모듈 자동 로딩과 실행 흐름

- `pkgutil.iter_modules()`로 `tools/`의 모듈을 탐색하고 `importlib.import_module()`로 불러옵니다.
- 모듈을 import하면 함수 정의에 붙은 `@tool`이 실행되어 도구가 등록됩니다.
- `registry`, `loader`, `autoload`처럼 기반 역할을 하는 모듈은 `tool_lab`의 자동 탐색 대상에서 제외합니다.
- `main.py`는 자동 로딩 후 `list`, `schema`, `call` 명령을 처리하는 실행 진입점입니다.

```text
main.py 실행
    → tools 모듈 탐색·import
    → @tool로 함수 등록
    → 도구 목록·명세 조회 또는 이름으로 호출
    → 결과를 JSON으로 출력
```

### 클래스와 상속

- 클래스는 속성과 동작을 정의하고, 인스턴스는 클래스로 만든 개별 객체입니다.
- 인스턴스 메서드의 `self`는 해당 인스턴스를 가리키며, `__init__()`에서 초기 상태를 설정합니다.
- 상속을 이용하면 기존 클래스의 기능을 재사용하고 확장할 수 있습니다.
- `super()`는 메서드 탐색 순서에 따라 상위 클래스의 메서드를 호출할 때 사용합니다.
- 오버라이딩은 상속받은 메서드를 자식 클래스에서 다시 정의하는 것입니다.

## 실습 내용

1. `test/`에서 `add`, `hello` 함수를 등록하고 도구 목록과 이름을 이용한 호출 구조를 살펴봅니다.
2. `tool_lab/`에서 `sales.csv`를 읽고 수량·가격을 변환하여 거래별 매출액을 계산합니다.
3. `summarize_sales()`로 전체 매출과 지역별 상위 매출을 집계합니다.
4. `region_detail()`로 특정 지역의 거래를 조회하고 최소 매출액 조건으로 필터링합니다.
5. 함수 정보로 명세를 생성하고, 데코레이터와 자동 import로 도구 등록을 구성합니다.
6. CLI에서 도구 목록 조회, 명세 조회, JSON 인자를 전달하는 호출 방법을 확인합니다.
7. 클래스·인스턴스·상속 관련 교안으로 객체지향 기초를 정리합니다.

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [test/](test/README.md) | 덧셈·인사 함수를 이용한 도구 자동 등록 기초 실습 |
| [tool_lab/](tool_lab/README.md) | CSV 매출 데이터와 도구 레지스트리를 이용한 CLI 실습 |
| [tool_lab/main.py](tool_lab/main.py) | `list`, `schema`, `call` 명령 처리 |
| [tool_lab/tools/loader.py](tool_lab/tools/loader.py) | CSV 로딩, 숫자 변환, 거래별 매출액 계산 |
| [tool_lab/tools/registry.py](tool_lab/tools/registry.py) | 도구 명세 생성, 데코레이터 등록, 이름으로 호출 |
| [tool_lab/tools/sales_tools.py](tool_lab/tools/sales_tools.py) | 전체 매출 요약과 지역별 거래 조회 |
| [tool_lab/tools/autoload.py](tool_lab/tools/autoload.py) | 도구 모듈 탐색과 자동 import |
| [tool_lab/sales.csv](tool_lab/sales.csv) | 매출 집계에 사용하는 실습 데이터 |
| [파이썬 구조 잡기 Part 1 교안](교안/python_구조잡기_part1_교안.html) | 반환값 설계, 함수 명세, 데코레이터, 모듈 구조와 CLI |
| [클래스·인스턴스·상속 교안](<교안/파이썬 클래스, 인스턴스, 메서드, super, 오버라이딩의 이해.html>) | 클래스, 메서드, 상속, `super()`, 오버라이딩 기초 |

## 실행 방법

Python 3.10 이상이 필요하며, 두 실습은 표준 라이브러리만 사용합니다. PowerShell에서 실행합니다.

```powershell
# 도구 자동 등록 기초 실습
cd C:\ai-starter\2026-10\10-06\test
python main.py

# 매출 집계 도구 목록과 명세 조회
cd C:\ai-starter\2026-10\10-06\tool_lab
python main.py list
python main.py schema summarize_sales
```

- 각 명령은 결과를 출력한 뒤 종료합니다.
- JSON 인자를 전달하는 `call` 예제는 [tool_lab README](tool_lab/README.md)를 참고합니다.
- 교안 HTML 파일은 웹 브라우저에서 엽니다.
