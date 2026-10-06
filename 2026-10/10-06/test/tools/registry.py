import inspect

TOOLS = {}


def tool(func):
    """함수를 도구로 등록하는 데코레이터"""

    sig = inspect.signature(func)

    schema = {
        "name": func.__name__,
        "description": func.__doc__ or "",
        "parameters": {
            name: str(param.annotation)
            for name, param in sig.parameters.items()
        }
    }

    TOOLS[func.__name__] = {
        "func": func,
        "schema": schema
    }

    return func


def list_tools():
    """등록된 도구 목록"""
    return [data["schema"] for data in TOOLS.values()]


def call_tool(name, args):
    """등록된 도구 실행"""
    return TOOLS[name]["func"](**args)