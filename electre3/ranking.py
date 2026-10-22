"""Main ranking pipeline for ELECTRE III."""
import numpy as np
from typing import Optional

from .accumulator import NetFlowAccumulator
from .block import compute_block
from .config import CriterionConfig, ComputeConfig
from .runtime import require_before_deadline
from .validate import validate_thresholds, normalize_weights, validate_matrix, validate_arrays_match


def compute_ranking(
    G: np.ndarray,
    criteria: list[CriterionConfig],
    config: Optional[ComputeConfig] = None,
    *,
    deadline: float | None = None,
) -> tuple[np.ndarray, NetFlowAccumulator]:
    """Compute a complete ranking, checking the supplied monotonic deadline per block.

    Minimize semantics remain the normalized transform ``1-g``. Pairwise calculation
    evaluates its equivalent directly as ``g(b)-g(a)`` to avoid loss from storing
    ``1-g`` near binary64 endpoints.
    """
    if not criteria:
        raise ValueError("criteria list cannot be empty")
    if config is None:
        config = ComputeConfig()
    validate_thresholds(criteria)
    weights = normalize_weights(criteria)
    validate_matrix(G, len(criteria))
    q = np.array([c.q for c in criteria], dtype=np.float64)
    p = np.array([c.p for c in criteria], dtype=np.float64)
    v = np.array([c.v for c in criteria], dtype=np.float64)
    directions = np.array([1.0 if c.maximize else -1.0 for c in criteria], dtype=np.float64)
    validate_arrays_match(q, p, v, weights)
    rows, block_size = G.shape[0], config.block_size
    accumulator = NetFlowAccumulator(rows)
    for row_start in range(0, rows, block_size):
        for column_start in range(0, rows, block_size):
            require_before_deadline(deadline)
            credibility = compute_block(
                G[row_start:min(row_start + block_size, rows)],
                G[column_start:min(column_start + block_size, rows)],
                q, p, v, weights, row_start == column_start, directions,
            )
            accumulator.update(credibility, row_start, column_start)
    require_before_deadline(deadline)
    return np.argsort(-accumulator.net_flow()), accumulator
