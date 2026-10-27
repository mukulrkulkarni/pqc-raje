"""Convert validated CSV numeric cores into NumPy matrices."""
from __future__ import annotations
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.matrix_csv.cli import run
from scripts.matrix_csv.core import convert
from scripts.matrix_csv.errors import ConversionError
from scripts.matrix_csv.input import read_csv_rows


def convert_csv_to_matrix(path: Path, *, delimiter=",", has_header=False, id_col=None, fill_empty=None):
    try:
        return convert(path, read_csv_rows, delimiter, has_header, id_col, fill_empty)
    except (OSError, csv.Error) as error:
        raise ConversionError(f"CSV read error: {error}") from error


def main(argv=None):
    return run(argv, convert_csv_to_matrix)


if __name__ == "__main__":
    raise SystemExit(main())
