"""Main ranking pipeline for ELECTRE III."""

import numpy as np
from typing import Optional

from .config import CriterionConfig, ComputeConfig
from .validate import validate_thresholds, normalize_weights, validate_matrix
from .accumulator import NetFlowAccumulator
from .block import compute_block


def compute_ranking(
    G: np.ndarray,
    criteria: list[CriterionConfig],
    config: Optional[ComputeConfig] = None,
) -> tuple[np.ndarray, NetFlowAccumulator]:
    """Compute complete ELECTRE III ranking.

    Args:
        G: Performance matrix of shape (N, C).
        criteria: List of criterion configurations.
        config: Optional computation settings.

    Returns:
        Tuple of (ranking, accumulator) where:
        - ranking: Indices of alternatives sorted by descending net flow
        - accumulator: NetFlowAccumulator with detailed flow data

    Raises:
        ValueError: If inputs are invalid.
    """
    if config is None:
        config = ComputeConfig()

    # Validate inputs
    validate_thresholds(criteria)
    weights = normalize_weights(criteria)
    validate_matrix(G, len(criteria))

    # Extract threshold arrays
    q = np.array([c.q for c in criteria], dtype=np.float64)
    p = np.array([c.p for c in criteria], dtype=np.float64)
    v = np.array([c.v for c in criteria], dtype=np.float64)

    # Handle direction (flip for cost criteria)
    G_adj = G.copy()
    for j, c in enumerate(criteria):
        if not c.maximize:
            G_adj[:, j] = -G_adj[:, j]

    # Initialize accumulator
    N = G.shape[0]
    acc = NetFlowAccumulator(N)

    # Block iteration
    B = config.block_size
    for rs in range(0, N, B):
        re = min(rs + B, N)
        for cs in range(0, N, B):
            ce = min(cs + B, N)

            S_block = compute_block(
                G_adj[rs:re, :],
                G_adj[cs:ce, :],
                q, p, v, weights,
                is_diagonal=(rs == cs),
            )
            acc.update(S_block, rs, cs)

    # Compute ranking (descending net flow)
    net_flow = acc.net_flow()
    ranking = np.argsort(-net_flow)

    return ranking, acc
