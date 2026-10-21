"""CLI execution functions for ELECTRE III."""
import numpy as np
from typing import Any

from .shared import compute_validated_ranking


def format_preview(matrix: np.ndarray, criteria: list[dict[str, Any]]) -> str:
    lines = ["=" * 60, "ELECTRE III Computation Preview", "=" * 60, "",
             f"Matrix: {matrix.shape[0]} alt × {matrix.shape[1]} crit, dtype={matrix.dtype}", "",
             "Statistics:", f"  Min={matrix.min():.4f}, Max={matrix.max():.4f}, Mean={matrix.mean():.4f}"]
    if np.isnan(matrix).any(): lines.append("⚠ WARNING: NaN values")
    if np.isinf(matrix).any(): lines.append("⚠ WARNING: Infinite values")
    lines.extend(["", f"Criteria ({len(criteria)}):"])
    for i, c in enumerate(criteria):
        lines.append(f"  {i+1}. {c.get('name', f'C{i}')}: w={c.get('weight',1)}, q={c.get('q',0)}, p={c.get('p',0)}, v={c.get('v',0)}")
    lines.extend(["", f"Comparisons: {matrix.shape[0]**2:,}", "", "=" * 60])
    return "\n".join(lines)


def run_ranking(matrix: np.ndarray, criteria_data: list[dict[str, Any]],
                block_size: int = 1000, quiet: bool = False) -> np.ndarray:
    """Run the shared strict CLI/web contract and return ranking indices.

    This compatibility function retains its historical return type. Use
    ``compute_validated_ranking`` when the net-flow vector is required.
    """
    if not quiet:
        print("Computing ranking...")
    result = compute_validated_ranking(matrix, criteria_data, block_size)
    if not quiet:
        print("Done.")
    return result.ranking
