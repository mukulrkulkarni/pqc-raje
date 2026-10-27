"""CSV input helpers."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .errors import ConversionError


def read_csv_rows(path: Path, delimiter: str) -> Iterable[list[str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.reader(handle, delimiter=delimiter):
                if row and not (len(row) == 1 and not row[0].strip()):
                    yield row
    except (OSError, csv.Error) as error:
        raise ConversionError(f"CSV read error: {error}") from error


def identifier_index(header: list[str] | None, id_col: str | None) -> int | None:
    if id_col is None:
        return None
    if header is not None and not id_col.isdigit():
        try:
            return header.index(id_col)
        except ValueError as error:
            raise ConversionError(f"ID column '{id_col}' not found in header") from error
    try:
        return int(id_col)
    except ValueError as error:
        raise ConversionError(f"Invalid --id-col '{id_col}'") from error
