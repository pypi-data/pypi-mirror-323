def full_qual_name(obj: object) -> str:
    name: str = obj.__module__ + "." + obj.__qualname__
    if callable(obj):
        name += "()"
    return name
