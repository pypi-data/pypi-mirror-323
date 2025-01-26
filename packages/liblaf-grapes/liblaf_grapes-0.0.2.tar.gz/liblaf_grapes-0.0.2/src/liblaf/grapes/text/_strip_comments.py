from collections.abc import Generator


def strip_comments(
    text: str,
    comments: str = "#",
    *,
    strip: bool = True,
    strip_empty_lines: bool = True,
) -> Generator[str, None, None]:
    for raw_line in text.splitlines():
        line: str = raw_line.split(comments, 1)[0]
        if strip:
            line = line.strip()
        if strip_empty_lines and not line:
            continue
        yield line
