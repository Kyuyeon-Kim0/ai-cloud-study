from tools.registry import tool


@tool
def hello(name: str) -> str:
    """이름을 받아 인사합니다."""
    return f"안녕하세요 {name}"