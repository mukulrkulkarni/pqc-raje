"""Convert a real-world CSV into a numeric matrix for ELECTRE III.

Problem this solves
- electre3/data.py::load_matrix uses np.loadtxt for CSV.
- np.loadtxt requires a clean numeric-only CSV (no headers, no ID columns).

This converter accepts common "messy" CSV forms, validates them, and emits:
- .npy float64 matrix for fast, strict loading
- optional cleaned numeric-only CSV

Design constraints
- Deterministic output.
- No new third-party dependencies.
- Clear error messages with line/column location.

Usage
  python scripts/convert_matrix_csv.py in.csv out/matrix.npy

Optional:
  --has-header            CSV has a header row.
  --id-col INDEX|name     Drop an ID column by index (0-based) or header name.
  --delimiter ","         CSV delimiter.
  --allow-empty           Allow empty cells (treated as error unless --fill-empty).
  --fill-empty VALUE      Replace empty cells with VALUE (float).
  --write-clean-csv PATH  Write a numeric-only CSV.

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
                # Preserve rows like ",," so we can raise on empty cells.
                if row is None:
                    continue
                # Skip truly blank lines only.
                if len(row) == 1 and row[0].strip() == "":
                    continue
                # Python's csv.reader can return [] for blank lines (common on Windows).
                if len(row) == 0:
                    continue
                yield row
    except (OSError, csv.Error) as e:
        raise ConversionError(f"CSV read error: {e}") from e


def convert_csv_to_matrix(
    path: Path,
    *,
    delimiter: str = ",",
    has_header: bool = False,
    id_col: Optional[str] = None,
    fill_empty: Optional[float] = None,
) -> np.ndarray:
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
        header = rows[0]
        rows = rows[1:]
        if not rows:
            raise ConversionError("CSV header present but no data rows")

    # Determine ID column index (if any)
    id_index: Optional[int] = None
    if id_col is not None:
        if header is not None and not id_col.isdigit():
            try:
                id_index = header.index(id_col)
            except ValueError as e:
                raise ConversionError(f"ID column '{id_col}' not found in header") from e
        else:
            try:
                id_index = int(id_col)
            except ValueError as e:
                raise ConversionError(f"Invalid --id-col '{id_col}'") from e

    # Enforce rectangular shape after dropping ID column
    expected_len: Optional[int] = None
    matrix: list[list[float]] = []

    for r_i, row in enumerate(rows, start=1 if not has_header else 2):
        work = row
        if id_index is not None:
            if id_index < 0 or id_index >= len(work):
                raise ConversionError(f"ID column index {id_index} out of range at row {r_i}")
            work = [c for j, c in enumerate(work) if j != id_index]

        # Rows like ",," (all empty cells) are invalid data rows.
        # They are not blank lines.
        if work and all(c.strip() == "" for c in work):
            raise ConversionError(f"Empty row at row {r_i}")

        if expected_len is None:
            expected_len = len(work)
            if expected_len == 0:
                raise ConversionError("Row has zero columns after dropping id column")
        if len(work) != expected_len:
            raise ConversionError(
                f"Non-rectangular CSV at row {r_i}: expected {expected_len} columns, got {len(work)}"
            )

        out_row = [
            _parse_float(cell, row=r_i, col=(c_i + 1), fill_empty=fill_empty)
            for c_i, cell in enumerate(work)
        ]
        matrix.append(out_row)

    arr = np.array(matrix, dtype=np.float64)
    if arr.ndim != 2:
        raise ConversionError("Internal error: matrix is not 2D")
    if arr.shape[0] < 1 or arr.shape[1] < 1:
        raise ConversionError(f"Matrix shape invalid: {arr.shape}")
    return arr


def write_clean_csv(path: Path, matrix: np.ndarray, delimiter: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=delimiter)
        for row in matrix.tolist():
            w.writerow(row)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Convert/validate CSV to numeric matrix")
    p.add_argument("input_csv", type=Path)
    p.add_argument("output_npy", type=Path)
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    p.add_argument("--has-header", action="store_true", help="Input CSV has a header row")
    p.add_argument("--id-col", help="Drop ID column by 0-based index or header name")
    p.add_argument("--fill-empty", type=float, help="Fill empty cells with this value")
    p.add_argument("--write-clean-csv", type=Path, help="Write numeric-only CSV")
    args = p.parse_args(argv)

    try:
        if not args.input_csv.exists():
            raise ConversionError(f"File not found: {args.input_csv}")
        matrix = convert_csv_to_matrix(
            args.input_csv,
            delimiter=args.delimiter,
            has_header=args.has_header,
            id_col=args.id_col,
            fill_empty=args.fill_empty,
        )
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
