import atexit
import contextlib
import functools
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from types import TracebackType
from typing import ParamSpec, Self, TypeVar

from loguru import logger

from liblaf import grapes

from . import TimerRecords, get_time

_P = ParamSpec("_P")
_T = TypeVar("_T")


class timer(Mapping[str, float], contextlib.AbstractContextManager):  # noqa: N801
    counters: Sequence[str]
    depth: int = 0
    label: str | None = None
    records: TimerRecords
    record_log_level: int | str | None = "DEBUG"
    report_log_level: int | str | None = "INFO"
    _start: dict[str, float]
    _end: dict[str, float]

    def __init__(
        self,
        label: str | None = None,
        *,
        counters: Sequence[str] = ["perf", "process"],
        log_at_exit: bool = True,
        record_log_level: int | str | None = "DEBUG",
        report_log_level: int | str | None = "INFO",
    ) -> None:
        self.label = label
        self.counters = counters
        self.record_log_level = record_log_level
        self.report_log_level = report_log_level
        self.records = TimerRecords()
        self._start = {}
        self._end = {}
        if log_at_exit:
            TIMERS.append(self)

    def __getitem__(self, key: str) -> float:
        return self._end[key] - self._start[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.counters)

    def __len__(self) -> int:
        return len(self.counters)

    def __enter__(self) -> Self:
        if self.label is None:
            self.label = grapes.caller_location(2)
        self.depth += 1
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.end()
        self.depth -= 1

    def __call__(self, fn: Callable[_P, _T]) -> Callable[_P, _T]:
        if self.label is None:
            self.label = grapes.full_qual_name(fn)

        @functools.wraps(fn)
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            self.depth += 1
            with self:
                ret: _T = fn(*args, **kwargs)
            self.depth -= 1
            return ret

        return wrapped

    def start(self) -> None:
        for time_name in self.counters:
            self._start[time_name] = get_time(time_name)

    def end(self) -> None:
        for name in self.counters:
            self._end[name] = get_time(name)
        self.records.append(self)
        self.depth += 1
        self.log_record()
        self.depth -= 1

    def log_record(self) -> None:
        if not self.record_log_level:
            return
        logger.opt(depth=self.depth + 1).log(self.record_log_level, self.human_record())

    def log_report(self) -> None:
        if not self.report_log_level:
            return
        logger.opt(depth=1).log(self.report_log_level, self.human_report())

    @property
    def elapsed(self) -> float:
        return next(iter(self.values()))

    def human_report(self) -> str:
        return self.records.report(self.label)

    def human_record(self) -> str:
        text: str = f"{self.label} > " if self.label else ""
        for k in self.counters:
            human: str = grapes.human_duration(self[k])
            text += f"{k}: {human}, "
        text = text.removesuffix(", ")
        return text

    def track(self, iterable: Iterable[_T]) -> Iterable[_T]:
        self.depth += 1
        if self.label is None:
            self.label = grapes.caller_location(2)
        for item in iterable:
            with self:
                yield item
        self.depth -= 1


TIMERS: list[timer] = []


def exit_hook() -> None:
    for timer in TIMERS:
        if timer.records.count <= 1:
            continue
        timer.log_report()


atexit.register(exit_hook)
