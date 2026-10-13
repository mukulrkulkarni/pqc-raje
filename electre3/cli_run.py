"""CLI execution functions for ELECTRE III."""

import numpy as np
from typing import Any

from .config import CriterionConfig, ComputeConfig
from .ranking import compute_ranking


def format_preview(matrix: np.ndarray, criteria: list[dict[str, Any]]) -> str:
    """Format a preview of the computation inputs.

    Args:
        matrix: Performance matrix.
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
    lines.append("")
    lines.append("Matrix statistics:")
    lines.append(f"  Min: {matrix.min():.4f}")
    lines.append(f"  Max: {matrix.max():.4f}")
    lines.append(f"  Mean: {matrix.mean():.4f}")

    # Warnings
    if np.isnan(matrix).any():
        lines.append("")
        lines.append("⚠ WARNING: Matrix contains NaN values")
    if np.isinf(matrix).any():
        lines.append("")
        lines.append("⚠ WARNING: Matrix contains infinite values")

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


def run_ranking(
    matrix: np.ndarray,
    criteria_data: list[dict[str, Any]],
    block_size: int = 1000,
    quiet: bool = False,
) -> np.ndarray:
    """Run ELECTRE III ranking computation.

    Args:
        matrix: Performance matrix (N, C).
        criteria_data: List of criterion dictionaries.
        block_size: Block size for computation.
        quiet: Suppress progress output.

    Returns:
        Ranking array (indices sorted by descending net flow).
    """
    # Convert criteria dicts to CriterionConfig objects
    criterion_configs = []
    for c in criteria_data:
        cfg = CriterionConfig(
            name=c.get("name", "unnamed"),
            weight=c.get("weight", 1.0),
            q=c.get("q", 0),
            p=c.get("p", 0),
            v=c.get("v", 0),
            maximize=c.get("maximize", True),
        )
        criterion_configs.append(cfg)

    compute_config = ComputeConfig(block_size=block_size)

    if not quiet:
        print("Computing ranking...")

    ranking, acc = compute_ranking(matrix, criterion_configs, compute_config)

    if not quiet:
        print(f"Done. Processed {acc.blocks_done} blocks.")

    return ranking
