"""CLI implementation for numeric CSV conversion."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from .errors import ConversionError


def parser():
    result = argparse.ArgumentParser(description="Convert validated CSV numeric cores to NumPy")
    result.add_argument("input_csv", type=Path)
    result.add_argument("output_npy", type=Path)
    result.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    result.add_argument("--has-header", action="store_true", help="Input CSV has a header row")
    result.add_argument("--id-col", help="Validate and remove ID column by 0-based index or header name")
    result.add_argument("--fill-empty", type=float, help="Fill empty numeric cells with this finite value")
    result.add_argument("--write-clean-csv", type=Path, help="Write numeric-only CSV")
    return result


def save(args, matrix: np.ndarray) -> None:
    args.output_npy.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output_npy, matrix)
    if args.write_clean_csv:
        args.write_clean_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.write_clean_csv.open("w", encoding="utf-8", newline="") as handle:
            csv.writer(handle, delimiter=args.delimiter).writerows(matrix.tolist())


def run(argv, convert) -> int:
    args = parser().parse_args(argv)
    try:
        if not args.input_csv.exists():
            raise ConversionError(f"File not found: {args.input_csv}")
        matrix = convert(args.input_csv, delimiter=args.delimiter, has_header=args.has_header, id_col=args.id_col, fill_empty=args.fill_empty)
    except ConversionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    save(args, matrix)
    print(f"OK: {matrix.shape[0]}x{matrix.shape[1]} float64 saved to {args.output_npy}")
    return 0
