"""Preview service for matrix inspection before computation."""

import numpy as np
from pathlib import Path
from typing import Any, Optional

from electre3.data import load_matrix


def get_matrix_preview(path: Path, max_rows: int = 10) -> Optional[dict[str, Any]]:
    """Get preview data for a matrix file.

    Args:
        path: Path to the matrix file.
        max_rows: Maximum rows to include in data preview.

    Returns:
        Preview data dictionary, or None if load fails.
    """
    try:
        matrix = load_matrix(path)
    except Exception:
        return None

    stats = _compute_stats(matrix)

    # Data preview (first N rows)
    preview_data = matrix[:max_rows].tolist()

    return {
        "shape": matrix.shape,
        "dtype": str(matrix.dtype),
        "stats": stats,
        "data": preview_data,
        "has_nan": bool(np.isnan(matrix).any()),
        "has_inf": bool(np.isinf(matrix).any()),
        "total_rows": matrix.shape[0],
        "preview_rows": len(preview_data),
    }


def _compute_stats(matrix: np.ndarray) -> dict[str, float]:
    """Compute summary statistics for matrix.

    Args:
        matrix: The performance matrix.

    Returns:
        Dictionary of statistics.
    """
    return {
        "min": float(matrix.min()),
        "max": float(matrix.max()),
        "mean": float(matrix.mean()),
        "std": float(matrix.std()),
    }


def format_preview_cli(matrix: np.ndarray, criteria: list[dict]) -> str:
    """Format preview for CLI display.

    Args:
        matrix: The performance matrix.
        criteria: List of criterion dictionaries.

    Returns:
        Formatted preview string.
    """
    lines = ["=" * 60]
    lines.append("ELECTRE III Computation Preview")
    lines.append("=" * 60)
    lines.append("")

    # Matrix info
    lines.append(f"Matrix shape: {matrix.shape[0]} alternatives × {matrix.shape[1]} criteria")
    lines.append(f"Matrix dtype: {matrix.dtype}")

    # Stats
    stats = _compute_stats(matrix)
    lines.append("")
    lines.append("Matrix statistics:")
    lines.append(f"  Min: {stats['min']:.4f}")
    lines.append(f"  Max: {stats['max']:.4f}")
    lines.append(f"  Mean: {stats['mean']:.4f}")
    lines.append(f"  Std: {stats['std']:.4f}")

    # Warnings
    if np.isnan(matrix).any():
        lines.append("")
        lines.append("WARNING: Matrix contains NaN values")
    if np.isinf(matrix).any():
        lines.append("")
        lines.append("WARNING: Matrix contains infinite values")

    # Criteria summary
    lines.append("")
    lines.append(f"Criteria: {len(criteria)}")
    for i, c in enumerate(criteria):
        name = c.get("name", f"Criterion {i}")
        weight = c.get("weight", 1)
        q = c.get("q", 0)
        p = c.get("p", 0)
        v = c.get("v", 0)
        lines.append(f"  {i+1}. {name}: w={weight}, q={q}, p={p}, v={v}")

    # Complexity estimate
    n = matrix.shape[0]
    pairs = n * n
    lines.append("")
    lines.append(f"Computation: {pairs:,} pairwise comparisons")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)
