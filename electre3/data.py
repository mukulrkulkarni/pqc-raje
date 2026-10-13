"""Data loading utilities for ELECTRE III."""
import numpy as np
from pathlib import Path
from typing import Union

def load_matrix(path: Union[str, Path]) -> np.ndarray:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path).astype(np.float64)
    elif suffix == ".npz":
        data = np.load(path)
        return data[list(data.keys())[0]].astype(np.float64)
    elif suffix == ".csv":
        return np.loadtxt(path, delimiter=",", dtype=np.float64)
    elif suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError:
            raise ImportError("pyarrow required for .parquet files")
        return pq.read_table(path).to_pandas().values.astype(np.float64)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
