"""Main ranking pipeline for ELECTRE III."""
import numpy as np
from typing import Optional
from .config import CriterionConfig, ComputeConfig
from .validate import validate_thresholds, normalize_weights, validate_matrix, validate_arrays_match
from .accumulator import NetFlowAccumulator
from .block import compute_block

def compute_ranking(
    G: np.ndarray, criteria: list[CriterionConfig], config: Optional[ComputeConfig] = None
) -> tuple[np.ndarray, NetFlowAccumulator]:
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
    validate_arrays_match(q, p, v, weights)
    G_adj = G.copy()
    for j, c in enumerate(criteria):
        if not c.maximize:
            G_adj[:, j] = -G_adj[:, j]
    N, B = G.shape[0], config.block_size
    acc = NetFlowAccumulator(N)
    for rs in range(0, N, B):
        for cs in range(0, N, B):
            S = compute_block(G_adj[rs:min(rs+B,N)], G_adj[cs:min(cs+B,N)], q, p, v, weights, rs==cs)
            acc.update(S, rs, cs)
    return np.argsort(-acc.net_flow()), acc
