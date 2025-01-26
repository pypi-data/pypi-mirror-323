import json
import os
from pathlib import Path
from typing import Any


def load_json(fpath: str | os.PathLike[str]) -> Any:
    fpath: Path = Path(fpath)
    with fpath.open() as fp:
        return json.load(fp)


def save_json(fpath: str | os.PathLike[str], data: Any) -> None:
    fpath: Path = Path(fpath)
    with fpath.open("w") as fp:
        json.dump(data, fp)
