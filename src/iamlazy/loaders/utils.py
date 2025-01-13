from pathlib import Path

import charset_normalizer
from markdownify import markdownify


def trim_and_filter_lines(text: str) -> str:
    """
    Trims whitespace from each line in the given text and filters out empty lines.

    Args:
        text (str): The input text containing multiple lines.

    Returns:
        str: A string with each line trimmed of leading and trailing whitespace and empty lines removed.
    """
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines += [stripped]
    return "\n".join(lines)


def html_to_markdown(content: str | bytes) -> str:
    if isinstance(content, bytes):
        content = str(charset_normalizer.from_bytes(content).best())

    md = markdownify(content, strip=["a", "img"])
    return trim_and_filter_lines(md)


def read_html_content(f: str | Path) -> str:
    content = str(charset_normalizer.from_path(f).best())

    md = markdownify(content, strip=["a", "img"])
    return trim_and_filter_lines(md)
