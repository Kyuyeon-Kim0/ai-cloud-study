import json
import sys

from tools.autoload import load_all
from tools.registry import call_tool, list_tools

def main() -> None:
    load_all()  # 도구 등록

    if len(sys.argv) < 2:
        print("사용법: python main.py [list | schema <도구> | call <도구> <JSON>]")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        for s in list_tools():
            print(f"{s['name']:<18} {s['description']}")

    elif cmd == "schema":
        target = next(s for s in list_tools() if s["name"] == sys.argv[2])
        print(json.dumps(target, ensure_ascii=False, indent=2))

    elif cmd == "call":
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(
            json.dumps(
                call_tool(sys.argv[2], args),
                ensure_ascii=False,
                indent=2
            )
        )

if __name__ == "__main__":
    main()
