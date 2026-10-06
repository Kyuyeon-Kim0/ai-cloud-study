import importlib
import pkgutil
from pathlib import Path

SKIP = {"registry", "loader", "autoload"}

def load_all() -> list[str]:
    """tools 패키지의 모든 모듈을 import한다."""
    pkg_dir = Path(__file__).resolve().parent
    loaded = []
    for info in pkgutil.iter_modules([pkg_dir]):
        if info.name in SKIP or info.name.startswith("_"):
            continue
        importlib.import_module(f"tools.{info.name}")
        loaded.append(info.name)
    return loaded