import os
from typing import Any, TypeVar

import pydantic

from liblaf import grapes

_C = TypeVar("_C", bound=pydantic.BaseModel)


def load_pydantic(
    fpath: str | os.PathLike[str], cls: type[_C], *, ext: str | None = None
) -> _C:
    data: Any = grapes.deserialize(fpath, ext=ext)
    return cls.model_validate(data)


def save_pydantic(
    fpath: str | os.PathLike[str], data: pydantic.BaseModel, *, ext: str | None = None
) -> None:
    grapes.serialize(fpath, data.model_dump(), ext=ext)
