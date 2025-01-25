import csv
import json
import sys
from io import StringIO
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import ParseError as TomlParseError

from .formats import FormatType

ResultType = dict | list[dict] | None
ResultPair = tuple[FormatType, ResultType]


def loads(content: str, fmt: FormatType) -> ResultPair:
    """
    Attempt to parse `content` as the specified format, or auto-detect if not given.
    Returns (FormatType, data).
    If unrecognized => (UNKNOWN, None or empty).
    """
    text = content.strip()
    if not text:
        return FormatType.UNKNOWN, None

    # If user forced a format, parse only that
    if fmt != FormatType.UNKNOWN:
        data = _load_string_forced(text, fmt)
        return fmt, data

    # 1) Try JSON
    parsed = _try_load_json(text)
    if parsed is not None:
        # If it's a list or dict => JSON
        return FormatType.JSON, parsed

    # 2) Try JSONL
    parsed = _try_load_jsonl(text)
    if parsed is not None:
        return FormatType.JSONL, parsed

    # 3) Try TOML
    parsed = _try_load_toml(text)
    if parsed is not None:
        return FormatType.TOML, parsed

    # 4) Try Delimited
    fmt, parsed = _try_load_delimited(text)
    if parsed is not None:
        return fmt, parsed

    # 5) Unknown
    return FormatType.UNKNOWN, None


def _load_string_forced(content: str, fmt: FormatType) -> Any:
    """ """
    if fmt == FormatType.JSON:
        return _try_load_json(content)
    elif fmt == FormatType.JSONL:
        return _try_load_jsonl(content)
    elif fmt == FormatType.TOML:
        return _try_load_toml(content)
    elif fmt in (FormatType.CSV, FormatType.TSV, FormatType.PSV):
        result = _try_load_delimited(content)
        if result is not None:
            return result[1]  # the rows
        return None
    else:
        return None


def load(
    path: str | Path,
    raise_on_error: bool = False,
) -> Any:
    """
    Load data from stdin (-) or a file path.
    """
    if path == "-":
        content = sys.stdin.read()
        (fmt, data) = loads(content, FormatType.UNKNOWN)
        if fmt == FormatType.UNKNOWN and raise_on_error:
            raise ValueError("Could not parse STDIN as any known format.")
        return data

    path = Path(path)

    if not path.exists():
        if raise_on_error:
            raise FileNotFoundError(f"File not found: {path}")
        return None

    if path.stat().st_size == 0:
        if raise_on_error:
            raise ValueError(f"File is empty: {path}")
        return None

    # guess from extension
    fmt = FormatType.from_path(path)
    content_str = path.read_text(encoding="utf-8")
    (fmt, data) = loads(content_str, fmt=fmt)

    if fmt == FormatType.UNKNOWN and raise_on_error:
        raise ValueError(f"Could not parse file: {path}")

    return data


# Private Functions


def _try_load_json(content: str) -> ResultType:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def _try_load_jsonl(content: str) -> ResultType:
    lines = content.splitlines(keepends=False)
    list_of_dicts = []

    for line in lines:
        try:
            obj = json.loads(line)
            list_of_dicts.append(obj)
        except json.JSONDecodeError:
            return None

    if list_of_dicts:
        return list_of_dicts

    return None


def _try_load_toml(content: str) -> ResultType:
    try:
        return tomlkit.parse(content)
    except TomlParseError:
        return None


def _try_load_delimited(content: str) -> ResultPair:
    """Load from CSV/TSV/PSV using a known delimiter. Returns list of dicts or None."""
    dialect = csv.Sniffer().sniff(content)
    f = StringIO(content)
    reader = csv.DictReader(f, dialect=dialect)
    data = list(reader)
    fmt = FormatType.from_delimiter(dialect.delimiter)
    return fmt, data
