"""Numeric CSV conversion core."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

import numpy as np

from electre3.shared import validate_identifiers
from .errors import ConversionError
from .input import identifier_index


def parse_float(cell: str, row: int, col: int, fill: float | None) -> float:
    raw = cell.strip()
    if not raw and fill is None:
        raise ConversionError(f"Empty cell at row {row}, col {col}")
    try:
        value = float(fill if not raw else raw)
    except ValueError as error:
        raise ConversionError(f"Non-numeric cell '{raw}' at row {row}, col {col}") from error
    if not np.isfinite(value):
        raise ConversionError(f"Non-finite value {value} at row {row}, col {col}")
    return value


def convert(path: Path, reader: Callable[[Path, str], Iterable[list[str]]], delimiter=",", has_header=False, id_col=None, fill_empty=None) -> np.ndarray:
    if fill_empty is not None and not np.isfinite(float(fill_empty)):
        raise ConversionError(f"fill_empty must be finite, got {fill_empty}")
    rows = list(reader(path, delimiter))
    if not rows:
        raise ConversionError("CSV has no data rows")
    header = rows.pop(0) if has_header else None
    if has_header and not rows:
        raise ConversionError("CSV header present but no data rows")
    index, width, matrix, identifiers = identifier_index(header, id_col), None, [], []
    for number, row in enumerate(rows, 2 if has_header else 1):
        if index is not None:
            if not 0 <= index < len(row):
                raise ConversionError(f"ID column index {index} out of range at row {number}")
            identifiers.append(row[index])
            row = [cell for column, cell in enumerate(row) if column != index]
        if not row or all(not cell.strip() for cell in row):
            raise ConversionError(f"Empty row at row {number}")
        if width is None:
            width = len(row)
        if len(row) != width:
            raise ConversionError(f"Non-rectangular CSV at row {number}: expected {width} columns, got {len(row)}")
        matrix.append([parse_float(cell, number, column + 1, fill_empty) for column, cell in enumerate(row)])
    if index is not None:
        try:
            validate_identifiers(identifiers)
        except ValueError as error:
            raise ConversionError(f"Invalid identifiers: {error}") from error
    array = np.array(matrix, dtype=np.float64)
    if array.ndim != 2 or 0 in array.shape:
        raise ConversionError(f"Matrix shape invalid: {array.shape}")
    return array
