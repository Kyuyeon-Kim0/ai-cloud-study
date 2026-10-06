# 파이썬 도구 자동 등록 실습

`@tool` 데코레이터로 함수를 등록하고, `tools` 폴더의 모듈을 자동으로 불러와 이름으로 실행하는 예제입니다. 파이썬 표준 라이브러리만 사용하므로 별도 패키지 설치는 필요하지 않습니다.

## 파일 구조

```text
test/
├── README.md
├── main.py              도구 로딩, 목록 출력, 실행 예제
└── tools/
    ├── registry.py      도구 등록 및 조회·실행
    ├── autoload.py      도구 모듈 자동 import
    ├── a.py             add: 두 숫자 더하기
    └── b.py             hello: 이름으로 인사하기
```

## 실행 방법

프로젝트 루트에서 실행합니다.

```powershell
python test/main.py
```

또는 `test` 폴더로 이동한 뒤 실행합니다.

```powershell
cd test
python main.py
```

등록된 `add`, `hello` 도구의 이름, 설명, 매개변수 타입을 출력한 다음, `add(a=10, b=20)`을 실행하여 `30`을 출력합니다.

## 동작 흐름

1. `main.py`에서 `load_all()`을 호출합니다.
2. `autoload.py`가 `tools` 폴더의 모듈을 탐색하고 import합니다. `registry`와 `autoload`는 탐색 대상에서 제외합니다.
3. 모듈을 import할 때 `@tool`이 실행되어 함수를 `TOOLS` 딕셔너리에 등록합니다.
4. `list_tools()`로 등록된 도구 정보를 조회합니다.
5. `call_tool(name, args)`로 도구 이름과 인자 딕셔너리를 전달하여 함수를 실행합니다.

`registry.py`는 함수 이름, docstring, 매개변수 타입 어노테이션으로 도구 정보를 만듭니다. 타입 어노테이션은 설명에 사용되며, 전달한 인자의 타입을 검사하지는 않습니다.

## 새 도구 추가

`tools` 폴더에 새 파이썬 파일을 만들고 함수에 `@tool`을 붙입니다.

```python
# tools/c.py
from tools.registry import tool


@tool
def multiply(a: int, b: int) -> int:
    """두 숫자를 곱합니다."""
    return a * b
```

다음 실행부터 `load_all()`이 새 모듈을 불러와 도구를 등록합니다. `main.py`의 `load_all()` 호출 이후에 다음 코드를 추가하면 실행할 수 있습니다.

```python
result = call_tool("multiply", {"a": 3, "b": 4})
print(result)  # 12
```

도구 이름은 함수 이름으로 정해집니다. 같은 이름을 다시 등록하면 기존 도구를 덮어쓰므로 서로 다른 이름을 사용하세요.

## 캐시 파일

실행 중 생성되는 `__pycache__` 폴더와 `*.pyc` 파일은 파이썬 바이트코드 캐시입니다. 직접 수정할 필요가 없으며, 삭제해도 필요할 때 다시 생성됩니다.
