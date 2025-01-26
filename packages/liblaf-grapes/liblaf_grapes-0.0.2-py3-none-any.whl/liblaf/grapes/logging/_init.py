import logging
from collections.abc import Sequence

import loguru

from . import init_icecream, init_loguru, init_rich


def init_logging(
    level: int | str = logging.NOTSET,
    *,
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    levels: Sequence["loguru.LevelConfig"] | None = None,
    traceback_show_locals: bool = True,
) -> None:
    init_rich(show_locals=traceback_show_locals)
    init_loguru(level=level, handlers=handlers, levels=levels)
    init_icecream()
