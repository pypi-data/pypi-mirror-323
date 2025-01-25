import csv
from enum import StrEnum
from os import PathLike
from pathlib import Path


class PipedDialect(csv.excel):
    delimiter = "|"


class FormatType(StrEnum):
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    TSV = "tsv"
    PSV = "psv"
    TOML = "toml"
    UNKNOWN = "unknown"

    @property
    def delimiter(self) -> str | None:
        """Return the default delimiter for CSV-like formats."""
        match self:
            case FormatType.TSV:
                return "\t"
            case FormatType.PSV:
                return "|"
            case FormatType.CSV:
                return ","
            case _:
                return None

    @property
    def dialect(self) -> type[csv.Dialect] | None:
        match self:
            case FormatType.TSV:
                return csv.excel_tab
            case FormatType.PSV:
                return PipedDialect
            case FormatType.CSV:
                return csv.excel
            case _:
                return None

    @classmethod
    def from_path(cls, path: PathLike | str) -> "FormatType":
        ext = Path(path).suffix.lower()[1:]
        try:
            return cls(ext)
        except ValueError:
            return cls.UNKNOWN

    @classmethod
    def from_delimiter(cls, delimiter: str) -> "FormatType":
        """
        Return the FormatType for the given delimiter.
        """
        match delimiter:
            case "\t":
                return cls.TSV
            case "|":
                return cls.PSV
            case ",":
                return cls.CSV
            case _:
                return cls.UNKNOWN
