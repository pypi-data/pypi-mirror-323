import collections
import textwrap
from collections.abc import Iterator, Mapping

from liblaf import grapes

with grapes.optional_imports(extra="timer"):
    import numpy as np
    import polars as pl


class TimerRecords(Mapping[str, list[float]]):
    _records: dict[str, list[float]]

    def __init__(self) -> None:
        self._records = collections.defaultdict(list)

    def __getitem__(self, key: str) -> list[float]:
        return self._records[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._records)

    def __len__(self) -> int:
        return len(self._records)

    def append(
        self,
        seconds: float | Mapping[str, float] = {},
        nanoseconds: float | Mapping[str, float] = {},
    ) -> None:
        if not isinstance(seconds, Mapping):
            seconds = {"perf": seconds}
        if not isinstance(nanoseconds, Mapping):
            nanoseconds = {"perf": nanoseconds}
        for k, v in seconds.items():
            self._records[k].append(v)
        for k, v in nanoseconds.items():
            self._records[k].append(v * 1e-9)

    @property
    def count(self) -> int:
        return len(next(iter(self._records.values()), []))

    def report(self, label: str | None = None) -> str:
        text: str = ""
        for k in self._records:
            text += f"{k} > "
            arr: np.ndarray = self.to_numpy(k)
            best_human: str = grapes.human_duration(arr.min())
            mean_human: str = grapes.human_duration_series(arr)
            text += f"best: {best_human}, mean: {mean_human}\n"
        text = text.strip()
        label = label or "Timer"
        text = f"{label} (total: {self.count})" + "\n" + textwrap.indent(text, "  ")
        return text

    def to_polars(self) -> pl.DataFrame:
        return pl.DataFrame(self._records)

    def to_numpy(self, key: str = "perf") -> np.ndarray:
        return np.asarray(self._records[key])
