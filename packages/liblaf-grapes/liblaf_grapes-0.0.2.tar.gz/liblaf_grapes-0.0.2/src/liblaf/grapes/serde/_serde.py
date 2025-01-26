import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from liblaf import grapes

READERS: dict[str, Callable[..., Any]] = {".json": grapes.load_json}
WRITERS: dict[str, Callable[..., None]] = {".json": grapes.save_json}
if grapes.has_module("tomlkit"):
    READERS[".toml"] = grapes.load_toml
    WRITERS[".toml"] = grapes.save_toml
if grapes.has_module("ruamel.yaml"):
    READERS[".yaml"] = grapes.load_yaml
    READERS[".yml"] = grapes.load_yaml
    WRITERS[".yaml"] = grapes.save_yaml
    WRITERS[".yml"] = grapes.save_yaml


def serialize(
    fpath: str | os.PathLike[str], data: Any, *, ext: str | None = None
) -> None:
    fpath: Path = Path(fpath)
    if ext is None:
        ext = fpath.suffix
    if ext not in WRITERS:
        msg: str = f"Unsupported file extension: {ext}"
        raise ValueError(msg)
    writer = WRITERS[ext]
    fpath.parent.mkdir(parents=True, exist_ok=True)
    writer(fpath, data)


def deserialize(fpath: str | os.PathLike[str], *, ext: str | None = None) -> Any:
    fpath: Path = Path(fpath)
    if ext is None:
        ext = fpath.suffix
    if ext not in READERS:
        msg: str = f"Unsupported file extension: {ext}"
        raise ValueError(msg)
    reader = READERS[ext]
    return reader(fpath)
