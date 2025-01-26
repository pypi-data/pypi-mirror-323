import math

from liblaf import grapes

with grapes.optional_imports(extra="human"):
    import numpy as np
    import numpy.typing as npt


UNITS: dict[str, float] = {
    "ns": 1e-9,
    "us": 1e-6,
    "ms": 1e-3,
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
    "y": 31536000,
}


def get_unit_seconds(unit: str) -> float:
    return UNITS[unit.lower()]


def human_duration_unit_precision(seconds: float) -> tuple[str, int]:  # noqa: C901, PLR0911, PLR0912
    if seconds <= 0:
        return "s", 0
    if seconds < 1e-09:
        return "ns", 3  # .999 ns
    if seconds < 1e-08:
        return "ns", 2  # 9.99 ns
    if seconds < 1e-07:
        return "ns", 1  # 99.9 ns
    if seconds < 1e-06:
        return "ns", 0  # 999. ns
    if seconds < 1e-05:
        return "us", 2  # 9.99 us
    if seconds < 1e-04:
        return "us", 1  # 99.9 us
    if seconds < 1e-03:
        return "us", 0  # 999. us
    if seconds < 1e-02:
        return "ms", 2  # 9.99 ms
    if seconds < 1e-01:
        return "ms", 1  # 99.9 ms
    if seconds < 1:
        return "ms", 0  # 999. ms
    if seconds < 10:
        return "s", 2  # 9.99 s
    if seconds < 60:
        return "s", 1  # 59.9 s
    if seconds < 3600:
        return "m", 0  # 59:59
    if seconds < 86400:
        return "h", 0  # 23:59:59
    return "h", 0


def human_duration(
    seconds: float, unit: str | None = None, precision: int | None = None
) -> str:
    if (unit is None) or (precision is None):
        unit, precision = human_duration_unit_precision(seconds)
    if unit in {"ns", "us", "ms", "s"}:
        unit_seconds: float = get_unit_seconds(unit)
        value: float = seconds / unit_seconds
        human: str = f"{value:.{precision}f}".lstrip("0")
        if precision == 0:
            human += "."
        if unit == "us":
            unit = "µs"
        human += f" {unit}"
        return human
    if unit == "m":
        minutes: int = int(seconds // 60)
        seconds %= 60
        return f"{minutes}:{seconds:02.0f}"
    hours: int = int(seconds // 3600)
    seconds %= 3600
    minutes: int = int(seconds // 60)
    seconds %= 60
    return f"{hours}:{minutes:02.0f}:{seconds:02.0f}"
    # TODO: handle longer durations


def human_duration_with_variance(mean: float, std: float) -> str:
    if not math.isfinite(std):
        return human_duration(mean)
    return human_duration(mean) + " ± " + human_duration(std)


def human_duration_series(series: npt.ArrayLike) -> str:
    series: npt.NDArray = np.asarray(series)
    if series.size <= 1:
        return human_duration(series.item())
    return human_duration_with_variance(series.mean(), series.std())
