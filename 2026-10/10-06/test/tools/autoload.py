import importlib
import pkgutil
import tools


def load_all():
    """tools 폴더의 모듈을 자동으로 import"""

    for module in pkgutil.iter_modules(tools.__path__):
        name = module.name

        if name in ("registry", "autoload"):
            continue

        importlib.import_module(f"tools.{name}")