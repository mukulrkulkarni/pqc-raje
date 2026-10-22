"""Convert CSV numeric cores into NumPy matrices for ELECTRE III.

The primary CLI accepts the approved identifier-bearing CSV contract directly:
``(N, C+1)`` with a string identifier in column zero and ``C`` numeric scores.
Use this converter only when a numeric NumPy core is required. The resulting ``.npy``
contains only ``(N, C)`` scores, so its later CLI identifiers are positional (``0``,
``1``, ...). Keep the original CSV when its source identifiers are needed.

Usage
  python scripts/convert_matrix_csv.py in.csv out/matrix.npy --has-header --id-col Asset

Exit codes
- 0 success
- 2 validation / parse error
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

from electre3.shared import validate_identifiers


class ConversionError(ValueError):
    pass


def _parse_float(cell: str, *, row: int, col: int, fill_empty: Optional[float]) -> float:
    raw = cell.strip()
    if raw == "":
        if fill_empty is None:
            raise ConversionError(f"Empty cell at row {row}, col {col}")
        val = float(fill_empty)
        if not np.isfinite(val):
            raise ConversionError(f"fill_empty must be finite, got {val}")
        return val
    try:
        val = float(raw)
    except ValueError as e:
        raise ConversionError(f"Non-numeric cell '{raw}' at row {row}, col {col}") from e
    if not np.isfinite(val):
        raise ConversionError(f"Non-finite value {val} at row {row}, col {col}")
    return val


def read_csv_rows(path: Path, delimiter: str) -> Iterable[list[str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if row is None or len(row) == 0:
                    continue
                if len(row) == 1 and row[0].strip() == "":
                    continue
                yield row
    except (OSError, csv.Error) as e:
        raise ConversionError(f"CSV read error: {e}") from e


def _identifier_index(header: Optional[list[str]], id_col: Optional[str]) -> Optional[int]:
    if id_col is None:
        return None
    if header is not None and not id_col.isdigit():
        try:
            return header.index(id_col)
        except ValueError as e:
            raise ConversionError(f"ID column '{id_col}' not found in header") from e
    try:
        return int(id_col)
    except ValueError as e:
        raise ConversionError(f"Invalid --id-col '{id_col}'") from e


def convert_csv_to_matrix(
    path: Path,
    *,
    delimiter: str = ",",
    has_header: bool = False,
    id_col: Optional[str] = None,
    fill_empty: Optional[float] = None,
) -> np.ndarray:
    """Validate CSV rows and return their numeric ``(N,C)`` core.

    When ``id_col`` is supplied, validate the removed identifier values using the
    shared non-empty, unique, control-character-free, maximum-50-character contract.
    """
    if fill_empty is not None and not np.isfinite(float(fill_empty)):
        raise ConversionError(f"fill_empty must be finite, got {fill_empty}")
    try:
        rows = list(read_csv_rows(path, delimiter))
    except (OSError, csv.Error) as e:
        raise ConversionError(f"CSV read error: {e}") from e
    if not rows:
        raise ConversionError("CSV has no data rows")

    header: Optional[list[str]] = None
    if has_header:
        header = rows.pop(0)
        if not rows:
            raise ConversionError("CSV header present but no data rows")

    id_index = _identifier_index(header, id_col)
    expected_len: Optional[int] = None
    matrix: list[list[float]] = []
    identifiers: list[str] = []

    for row_number, row in enumerate(rows, start=2 if has_header else 1):
        if id_index is not None:
            if id_index < 0 or id_index >= len(row):
                raise ConversionError(f"ID column index {id_index} out of range at row {row_number}")
            identifiers.append(row[id_index])
            work = [cell for index, cell in enumerate(row) if index != id_index]
        else:
            work = row
        if work and all(cell.strip() == "" for cell in work):
            raise ConversionError(f"Empty row at row {row_number}")
        if expected_len is None:
            expected_len = len(work)
            if expected_len == 0:
                raise ConversionError("Row has zero columns after dropping id column")
        if len(work) != expected_len:
            raise ConversionError(
                f"Non-rectangular CSV at row {row_number}: expected {expected_len} columns, got {len(work)}"
            )
        matrix.append([
            _parse_float(cell, row=row_number, col=index + 1, fill_empty=fill_empty)
            for index, cell in enumerate(work)
        ])

    if id_index is not None:
        try:
            validate_identifiers(identifiers)
        except ValueError as e:
            raise ConversionError(f"Invalid identifiers: {e}") from e
    array = np.array(matrix, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise ConversionError(f"Matrix shape invalid: {array.shape}")
    return array


def write_clean_csv(path: Path, matrix: np.ndarray, delimiter: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(matrix.tolist())


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Convert validated CSV numeric cores to NumPy")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_npy", type=Path)
    parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    parser.add_argument("--has-header", action="store_true", help="Input CSV has a header row")
    parser.add_argument("--id-col", help="Validate and remove ID column by 0-based index or header name")
    parser.add_argument("--fill-empty", type=float, help="Fill empty numeric cells with this finite value")
    parser.add_argument("--write-clean-csv", type=Path, help="Write numeric-only CSV")
    args = parser.parse_args(argv)
    try:
        if not args.input_csv.exists():
            raise ConversionError(f"File not found: {args.input_csv}")
        matrix = convert_csv_to_matrix(args.input_csv, delimiter=args.delimiter, has_header=args.has_header,
                                       id_col=args.id_col, fill_empty=args.fill_empty)
    except ConversionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    args.output_npy.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output_npy, matrix)
    if args.write_clean_csv is not None:
        args.write_clean_csv.parent.mkdir(parents=True, exist_ok=True)
        write_clean_csv(args.write_clean_csv, matrix, args.delimiter)
    print(f"OK: {matrix.shape[0]}x{matrix.shape[1]} float64 saved to {args.output_npy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
