import functools

from environs import Env


@functools.lru_cache
def init_env(prefix: str | None = "LIBLAF_") -> Env:
    env = Env(prefix=prefix)
    env.read_env()
    return env
