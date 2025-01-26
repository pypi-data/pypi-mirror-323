import os
from pathlib import Path
from typing import Any

import etils.epy


def callback(exc: ImportError) -> None:
    etils.epy.reraise(
        exc,
        suffix=f"""Missing optional dependency {exc.name}.
Make sure to install liblaf.grapes using `pip install liblaf.grapes[toml]`.""",
    )


with etils.epy.lazy_imports(
    error_callback="Make sure to install `liblaf.grapes` using `pip install liblaf.grapes[toml]`."
):
    import tomlkit


def load_toml(fpath: str | os.PathLike[str]) -> tomlkit.TOMLDocument:
    fpath: Path = Path(fpath)
    with fpath.open() as fp:
        return tomlkit.load(fp)


def save_toml(
    fpath: str | os.PathLike[str], data: Any, *, sort_keys: bool = False
) -> None:
    fpath: Path = Path(fpath)
    with fpath.open("w") as fp:
        tomlkit.dump(data, fp, sort_keys=sort_keys)
