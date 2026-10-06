from tools.registry import tool


@tool
def add(a: int, b: int) -> int:
    """두 숫자를 더합니다."""
    return a + b