from liblaf import grapes

with grapes.optional_imports(extra="duration"):
    import about_time


def human_count(count: int, unit: str = "", prec: int | None = None) -> str:
    # TODO: remove dependency on `about-time`
    hc = about_time.HumanCount(count, unit)
    return hc.as_human(prec)
