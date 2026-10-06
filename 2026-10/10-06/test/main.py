import json

from tools.autoload import load_all
from tools.registry import list_tools, call_tool


load_all()


print("=== 등록된 도구 ===")

print(
    json.dumps(
        list_tools(),
        ensure_ascii=False,
        indent=2
    )
)


print("\n=== 도구 실행 ===")

result = call_tool(
    "add",
    {
        "a": 10,
        "b": 20
    }
)

print(result)