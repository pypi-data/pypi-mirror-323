import functools

import rich.pretty
import rich.traceback
from rich.console import Console
from rich.style import Style
from rich.theme import Theme


@functools.cache
def logging_theme() -> Theme:
    """...

    References:
        [1] [loguru/loguru/_defaults.py at c490ce0534c6e176306f339a92c221dc6f41a6a7 · Delgan/loguru](https://github.com/Delgan/loguru/blob/c490ce0534c6e176306f339a92c221dc6f41a6a7/loguru/_defaults.py)
    """
    return Theme(
        {
            "logging.level.notset": Style(dim=True),
            "logging.level.trace": Style(color="cyan", bold=True),
            "logging.level.debug": Style(color="blue", bold=True),
            "logging.level.icecream": Style(color="magenta", bold=True),
            "logging.level.info": Style(bold=True),
            "logging.level.success": Style(color="green", bold=True),
            "logging.level.warning": Style(color="yellow", bold=True),
            "logging.level.error": Style(color="red", bold=True),
            "logging.level.critical": Style(color="red", bold=True, reverse=True),
        }
    )


@functools.cache
def logging_console() -> Console:
    return rich.console.Console(theme=logging_theme(), stderr=True)


def init_rich(*, show_locals: bool = True) -> None:
    rich.pretty.install(console=logging_console())
    rich.traceback.install(console=logging_console(), show_locals=show_locals)
