import contextlib
from collections.abc import Generator
from typing import Any

import etils.epy


@contextlib.contextmanager
def optional_imports(
    name: str = "liblaf.grapes", extra: str | None = None
) -> Generator[None, Any, None]:
    try:
        yield
    except ImportError as exc:
        suffix: str = f"Missing optional dependency `{exc.name}`."
        if extra is not None:
            suffix += (
                f"\nMake sure to install `{name}` using `pip install {name}[{extra}]`."
            )
        etils.epy.reraise(exc, suffix=suffix)
