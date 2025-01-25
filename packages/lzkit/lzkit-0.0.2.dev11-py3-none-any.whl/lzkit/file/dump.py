import csv
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import tomlkit

from . import FormatType


def dump(
    path: str | Path,
    data: dict | list[dict],
    *,
    # Format-specific options
    indent: int | None = None,
    sort_keys: bool = False,
    fieldnames: list[Any] | None = None,
    # General options
    raise_on_error: bool = False,
) -> bool:
    """
    :param path: Output file path.
    :param data: The data to write.
    :param indent: For JSON, how many spaces to indent (None => no pretty-print).
    :param sort_keys: For JSON, whether to sort dictionary keys.
    :param fieldnames: For CSV-like formats, the column headers to use.
    :param raise_on_error: If True, raise exceptions on error; else return False.
    :return: True on success, or False if an error occurs (unless raise_on_error).
    """
    path = Path(path)
    fmt = FormatType.from_path(path)
    success = True

    # noinspection PyBroadException
    try:
        if fmt == FormatType.JSON:
            _dump_json(path, data, indent=indent, sort_keys=sort_keys)
        elif fmt == FormatType.JSONL:
            _dump_jsonl(path, data)
        elif (
            fmt == FormatType.CSV
            or fmt == FormatType.TSV
            or fmt == FormatType.PSV
        ):
            _dump_delimited(path, data, fmt, fieldnames=fieldnames)
        elif fmt == FormatType.TOML:
            _dump_toml(path, data)
        else:
            if raise_on_error:
                raise ValueError(f"Unsupported file extension: {path.suffix}")
            success = False

    except Exception:
        if raise_on_error:
            raise
        success = False

    return success


def _dump_json(
    path: Path,
    data: Any,
    *,
    indent: int | None,
    sort_keys: bool,
) -> None:
    """Write `data` to path in JSON format."""
    with path.open("w") as f:
        json.dump(data, f, indent=indent, sort_keys=sort_keys)


def _dump_jsonl(path: Path, data: Any) -> None:
    """
    JSON lines expects a list of objects, each on its own line.
    """
    if not isinstance(data, list):
        raise ValueError("JSONL dump requires a list of objects (list[dict]).")

    with path.open("w", encoding="utf-8") as f:
        for obj in data:
            line = json.dumps(obj)
            f.write(line + "\n")


def _dump_toml(path: Path, data: Any) -> None:
    """Write `data` to path in TOML format."""
    with path.open("w", encoding="utf-8") as f:
        tomlkit.dump(data, f)


def _dump_delimited(
    path: Path,
    data: Any,
    fmt: FormatType,
    fieldnames: list[Any] | None = None,
):
    """
    For CSV, TSV, PSV. Expects data to be list[dict].
    """
    if not isinstance(data, list):
        raise ValueError("Delimited dump requires a list of dicts.")

    if not fieldnames and not data:
        raise ValueError("Dump requires minimum of data and/or fieldnames")

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with path.open("w", newline="", encoding="utf-8") as f:
        dialect = fmt.dialect or csv.excel
        # noinspection PyTypeChecker
        writer = csv.DictWriter(f, fieldnames, dialect=dialect)
        writer.writeheader()
        writer.writerows(data)


def dumps(
    data: Any,
    format_type: FormatType,
    *,
    indent: int | None = None,
    sort_keys: bool = False,
    fieldnames: Sequence[str] | None = None,
) -> str:
    """
    :param data: The data to format. Must match expectations (list vs dict).
    :param format_type: One of FormatType.
    :param indent: JSON indentation.
    :param sort_keys: Whether to sort JSON keys.
    :param fieldnames: CSV/TSV/PSV column headers; optional if data is nonempty.
    :return: A string representation of the data.
    """
    if format_type == FormatType.JSON:
        return _dumps_json(data, indent=indent, sort_keys=sort_keys)

    elif format_type == FormatType.JSONL:
        return _dumps_jsonl(data)

    elif format_type == FormatType.TOML:
        # If you need a trailing newline, add it after tomlkit.dumps(...)
        return tomlkit.dumps(data)

    elif format_type in (FormatType.CSV, FormatType.TSV, FormatType.PSV):
        return _dump_delimited_to_string(
            data,
            format_type,
            fieldnames=fieldnames,
        )

    # If unknown or data is empty, you can handle it gracefully:
    return ""


def _dumps_json(data: Any, *, indent: int | None, sort_keys: bool) -> str:
    return json.dumps(data, indent=indent, sort_keys=sort_keys)


def _dumps_jsonl(data: Any) -> str:
    if not data:
        return ""
    if not isinstance(data, list):
        raise ValueError("JSONL dump requires a list of objects.")
    return "\n".join(json.dumps(row) for row in data)


def _dump_delimited_to_string(
    data: list[dict],
    format_type: FormatType,
    *,
    fieldnames: Sequence[str] | None,
) -> str:
    """
    Return a CSV/TSV/PSV string from data.
    """
    import io

    if not isinstance(data, list):
        raise ValueError("Delimited string dump requires a list of dicts.")

    if not data and fieldnames is None:
        # If there's no data, you must at least provide headers to write
        raise ValueError(
            "Empty data and no fieldnames => can't produce header."
        )

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    if format_type == FormatType.TSV:
        delimiter = "\t"
    elif format_type == FormatType.PSV:
        delimiter = "|"
    else:
        delimiter = ","

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(data)
    return buf.getvalue().rstrip("\n")
