"""Typed matrix input loading utilities for ELECTRE III."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Union

import numpy as np

from .shared import validate_csv_headers, validate_identifiers, validate_score_matrix


@dataclass(frozen=True)
class MatrixInput:
    """Validated numeric scores plus stable row identifiers for one input matrix."""

    scores: np.ndarray
    identifiers: tuple[str, ...]
    identifier_header: str


def _positional(matrix: np.ndarray) -> MatrixInput:
    scores = np.asarray(matrix, dtype=np.float64)
    if scores.ndim != 2:
        raise ValueError("matrix must be 2D")
    return MatrixInput(scores, tuple(str(index) for index in range(scores.shape[0])), "Asset ID")


def _load_csv(path: Path, criteria: Sequence[object], header_mode: str | None) -> MatrixInput:
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError("CSV must be valid UTF-8 text") from exc
    if not rows:
        raise ValueError("CSV contains no rows")
    criterion_count = len(criteria)
    if header_mode not in {None, "headered", "headerless"}:
        raise ValueError("header_mode must be 'headered' or 'headerless'")
    is_headered = header_mode == "headered"
    if header_mode is None and len(rows[0]) == criterion_count + 1:
        is_headered = [getattr(criterion, "name", None) for criterion in criteria] == rows[0][1:]
    data_rows = rows[1:] if is_headered else rows
    identifier_header = rows[0][0] if is_headered else "Asset ID"
    if is_headered:
        validate_csv_headers(rows[0], criteria)
    identifiers: list[str] = []
    values: list[list[float]] = []
    for row_number, row in enumerate(data_rows, start=2 if is_headered else 1):
        if len(row) != criterion_count + 1:
            raise ValueError(f"CSV row {row_number} has {len(row)} columns, expected {criterion_count + 1}")
        identifiers.append(row[0])
        try:
            values.append([float(value) for value in row[1:]])
        except ValueError as exc:
            raise ValueError(f"CSV row {row_number} contains a non-numeric score") from exc
    validate_identifiers(identifiers)
    return MatrixInput(validate_score_matrix(values, criterion_count), tuple(identifiers), identifier_header)


def load_input(path: Union[str, Path], criteria: Sequence[object], *, header_mode: str | None = None) -> MatrixInput:
    """Load CSV identifiers or positional identifiers for numeric NumPy matrices."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _load_csv(path, criteria, header_mode)
    if suffix == ".npy":
        return _positional(np.load(path, allow_pickle=False))
    if suffix == ".npz":
        with np.load(path, allow_pickle=False) as archive:
            keys = list(archive.keys())
            if len(keys) != 1:
                raise ValueError("NPZ input must contain exactly one array")
            return _positional(archive[keys[0]])
    raise ValueError(f"Unsupported file format: {suffix}")


def load_matrix(path: Union[str, Path]) -> np.ndarray:
    """Legacy numeric-only loader; CSV identifiers require :func:`load_input`."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path, allow_pickle=False).astype(np.float64)
    if suffix == ".npz":
        with np.load(path, allow_pickle=False) as archive:
            return archive[list(archive.keys())[0]].astype(np.float64)
    if suffix == ".csv":
        return np.loadtxt(path, delimiter=",", dtype=np.float64)
    if suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise ImportError("pyarrow required for .parquet files") from exc
        return pq.read_table(path).to_pandas().values.astype(np.float64)
    raise ValueError(f"Unsupported file format: {suffix}")
