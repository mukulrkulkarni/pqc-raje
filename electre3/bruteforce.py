"""Brute-force reference implementation for testing."""

import numpy as np
from .config import CriterionConfig
from .validate import normalize_weights


def bruteforce_ranking(G: np.ndarray, criteria: list[CriterionConfig]) -> np.ndarray:
    """Compute ELECTRE III ranking without blocking (for testing).

    This is an O(N²) memory implementation for correctness verification.
    """
    N, C = G.shape
    weights = normalize_weights(criteria)
    q = np.array([c.q for c in criteria])
    p = np.array([c.p for c in criteria])
    v = np.array([c.v for c in criteria])

    # Adjust for direction
    G_adj = G.copy()
    for j, c in enumerate(criteria):
        if not c.maximize:
            G_adj[:, j] = -G_adj[:, j]

    # Full credibility matrix
    S = np.zeros((N, N))
    for a in range(N):
        for b in range(N):
            if a == b:
                continue
            diff = G_adj[a] - G_adj[b]
            c_j = _partial_conc(diff, q, p)
            C_ab = np.dot(c_j, weights)
            d_j = _disc(diff, p, v)
            S[a, b] = _cred(C_ab, d_j)

    net_flow = S.sum(axis=1) - S.sum(axis=0)
    return np.argsort(-net_flow)


def _partial_conc(diff, q, p):
    c = np.ones_like(diff)
    c[diff <= -p] = 0.0
    mask = (diff > -p) & (diff < -q)
    c[mask] = (diff[mask] + p[mask]) / np.maximum(p[mask] - q[mask], 1e-10)
    return c


def _disc(diff, p, v):
    d = np.zeros_like(diff)
    d[diff <= -v] = 1.0
    mask = (diff > -v) & (diff < -p)
    d[mask] = (-diff[mask] - p[mask]) / np.maximum(v[mask] - p[mask], 1e-10)
    return d


def _cred(C_ab, d_j):
    S = C_ab
    for d in d_j:
        if d > C_ab:
            S *= (1 - d) / max(1 - C_ab, 1e-10)
    return max(0, min(1, S))
