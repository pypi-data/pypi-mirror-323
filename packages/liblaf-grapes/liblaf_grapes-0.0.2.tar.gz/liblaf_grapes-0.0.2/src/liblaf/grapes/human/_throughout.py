from liblaf import grapes

with grapes.optional_imports(extra="duration"):
    import about_time


def human_throughout(value: float, unit: str = "", prec: int | None = None) -> str:
    # TODO: remove dependency on `about-time`
    ht = about_time.HumanThroughput(value, unit)
    return ht.as_human(prec)
