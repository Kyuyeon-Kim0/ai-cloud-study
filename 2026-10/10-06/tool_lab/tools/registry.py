import functools
import inspect
from typing import Any, Callable, get_type_hints

REGISTRY: dict[str, Callable] = {}

JSON_TYPE = {int: "integer", float: "number", str: "string",
             bool: "boolean", list: "array", dict: "object"}

def build_schema(func: Callable) -> dict:
    """함수 시그니처와 독스트링으로 도구 명세를 만든다."""
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    props, required = {}, []

    for name, param in sig.parameters.items():
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        hint = hints.get(name, str)
        props[name] = {"type": JSON_TYPE.get(hint, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(name)
        else:
            props[name]["default"] = param.default

    doc = (func.__doc__ or "").strip().split("\n")[0]
    return {
        "name": func.__name__,
        "description": doc,
        "parameters": {
            "type": "object",
            "properties": props,
            "required": required,
        },
    }

def tool(func: Callable) -> Callable:
    """이 함수를 도구로 등록한다."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.schema = build_schema(func)
    REGISTRY[func.__name__] = wrapper
    return wrapper


def list_tools() -> list[dict]:
    return [f.schema for f in REGISTRY.values()]


def call_tool(name: str, arguments: dict | None = None) -> Any:
    if name not in REGISTRY:
        raise KeyError(f"없는 도구: {name} (가능: {', '.join(REGISTRY)})")
    return REGISTRY[name](**(arguments or {}))
