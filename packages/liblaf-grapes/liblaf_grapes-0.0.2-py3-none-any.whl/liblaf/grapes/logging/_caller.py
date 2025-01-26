from pathlib import Path
from types import FrameType

from loguru._get_frame import get_frame


def caller_location(depth: int = 1, *, markup: bool = True) -> str:
    frame: FrameType | None = get_frame(depth)
    if not frame:
        return "<unknown>"
    filepath: Path = Path(frame.f_code.co_filename)
    if markup:
        filename: str = f"[link={filepath.as_uri()}]{filepath.name}[/link]"
        lineno: str = (
            f"[link={filepath.as_uri()}#{frame.f_lineno}]{frame.f_lineno}[/link]"
        )
    else:
        filename = filepath.name
        lineno = str(frame.f_lineno)
    return f"{filename}:{lineno}"
