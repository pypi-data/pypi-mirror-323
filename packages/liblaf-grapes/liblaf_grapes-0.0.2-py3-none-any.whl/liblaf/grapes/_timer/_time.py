import os
import time
from typing import Literal

type CounterName = Literal[
    "monotonic",
    "perf",
    "process",
    "time",
    "thread",
    "user",
    "system",
    "children_user",
    "children_system",
    "elapsed",
]


def get_time(name: CounterName | str = "perf") -> float:  # noqa: C901, PLR0911
    match name:
        case "monotonic":
            return time.monotonic()
        case "perf":
            return time.perf_counter()
        case "process":
            return time.process_time()
        case "time":
            return time.time()
        case "thread":
            return time.thread_time()
        case "user":
            return os.times().user
        case "system":
            return os.times().system
        case "children_user":
            return os.times().children_user
        case "children_system":
            return os.times().children_system
        case "elapsed":
            return os.times().elapsed
        case _:
            msg: str = f"Unsupported time: `{name}`"
            raise ValueError(msg)
