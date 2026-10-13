"""Data loading utilities for ELECTRE III."""

import numpy as np
from pathlib import Path
from typing import Union


def load_matrix(path: Union[str, Path]) -> np.ndarray:
    """Load performance matrix from file.

    Supports:
    - .npy: NumPy binary format
    - .npz: NumPy compressed format (uses first array)
    - .csv: Comma-separated values
    - .parquet: Apache Parquet (requires pyarrow)

    Args:
        path: Path to data file.

    Returns:
        Performance matrix as float64 array.

    Raises:
        ValueError: If file format is unsupported.
        FileNotFoundError: If file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".npy":
        return np.load(path).astype(np.float64)

    elif suffix == ".npz":
        data = np.load(path)
        key = list(data.keys())[0]
        return data[key].astype(np.float64)

    elif suffix == ".csv":
        return np.loadtxt(path, delimiter=",", dtype=np.float64)

    elif suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError:
            raise ImportError("pyarrow required for .parquet files")
        table = pq.read_table(path)
        return table.to_pandas().values.astype(np.float64)

    else:
        raise ValueError(f"Unsupported file format: {suffix}")
