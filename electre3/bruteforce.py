"""Brute-force reference implementation for testing."""
import numpy as np
from .config import CriterionConfig
from .validate import normalize_weights

def bruteforce_ranking(G: np.ndarray, criteria: list[CriterionConfig]) -> np.ndarray:
    N = G.shape[0]
    weights = normalize_weights(criteria)
    q, p, v = [np.array([c.q for c in criteria]) for _ in range(1)] + \
              [np.array([c.p for c in criteria]), np.array([c.v for c in criteria])]
    G_adj = G.copy()
    for j, c in enumerate(criteria):
        if not c.maximize: G_adj[:, j] = -G_adj[:, j]
    S = np.zeros((N, N))
    for a in range(N):
        for b in range(N):
            if a == b: continue
            diff = G_adj[a] - G_adj[b]
            c_j = _conc(diff, q, p)
            d_j = _disc(diff, p, v)
            S[a, b] = _cred(np.dot(c_j, weights), d_j)
    return np.argsort(-(S.sum(axis=1) - S.sum(axis=0)))

def _conc(diff, q, p):
    c = np.ones_like(diff)
    c[diff <= -p] = 0.0
    m = (diff > -p) & (diff < -q)
    c[m] = (diff[m] + p[m]) / np.maximum(p[m] - q[m], 1e-10)
    return c

def _disc(diff, p, v):
    d = np.zeros_like(diff)
    d[diff <= -v] = 1.0
    m = (diff > -v) & (diff < -p)
    d[m] = (-diff[m] - p[m]) / np.maximum(v[m] - p[m], 1e-10)
    return d

def _cred(C, d_j):
    S = C
    for d in d_j:
        if d > C: S *= (1 - d) / max(1 - C, 1e-10)
    return max(0, min(1, S))
