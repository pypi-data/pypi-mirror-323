import importlib
import importlib.util


def has_module(name: str, package: str | None = None) -> bool:
    return importlib.util.find_spec(name, package) is not None
