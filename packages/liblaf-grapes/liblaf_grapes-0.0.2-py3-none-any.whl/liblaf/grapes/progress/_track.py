from collections.abc import Generator, Iterable
from typing import Any, TypeVar

from rich.console import RenderableType
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Column
from rich.text import Text

from liblaf import grapes


class RateColumn(ProgressColumn):
    unit: str = "it"

    def __init__(self, unit: str = "it", table_column: Column | None = None) -> None:
        super().__init__(table_column)
        self.unit = unit

    def render(self, task: Task) -> RenderableType:
        if not task.speed:
            return Text(f"?{self.unit}/s", style="progress.data.speed")
        human: str = grapes.human_throughout(task.speed, self.unit)
        return Text(human, style="progress.data.speed")


_T = TypeVar("_T")


def track(
    sequence: Iterable[_T],
    *,
    description: str | bool | None = True,
    timer: bool = True,
    record_log_level: int | str | None = "DEBUG",
    report_log_level: int | str | None = "INFO",
) -> Generator[_T, Any, None]:
    columns: list[ProgressColumn] = [SpinnerColumn()]
    if description is True:
        description = grapes.caller_location(2)
    description = description or ""
    if description:
        columns.append(TextColumn("[progress.description]{task.description}"))
    columns += [
        BarColumn(),
        TaskProgressColumn(show_speed=True),
        MofNCompleteColumn(),
        "[",
        TimeElapsedColumn(),
        "<",
        TimeRemainingColumn(),
        ",",
        RateColumn(),
        "]",
    ]
    progress = Progress(*columns, console=grapes.logging_console())
    if timer:
        t = grapes.timer(
            label=description,
            log_at_exit=False,
            record_log_level=record_log_level,
            report_log_level=report_log_level,
        )
        with progress:
            yield from t.track(progress.track(sequence, description=description))
            t.log_report()
    else:
        with progress:
            yield from progress.track(sequence, description=description)
