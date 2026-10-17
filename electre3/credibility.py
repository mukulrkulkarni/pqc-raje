"""Credibility computation for ELECTRE III."""

import numpy as np


def credibility(C_ab: np.ndarray, d_j: np.ndarray) -> np.ndarray:
    """Compute credibility S(a,b) from concordance and discordance.

    Formula:
        S(a,b) = C(a,b) × ∏ F_j(a,b)

    Where:
        F_j(a,b) = 1                         if d_j(a,b) <= C(a,b)
        F_j(a,b) = (1 - d_j(a,b))/(1 - C(a,b))  otherwise

    Edge cases:
        - If any d_j >= 1: S = 0 (full veto, including when C(a,b) = 1)
        - If C(a,b) = 1 and all finite d_j < 1: S = 1

    Args:
        C_ab: Global concordance values, shape (B1, B2).
        d_j: Discordance values per criterion, shape (B1, B2, C).

    Returns:
        Credibility values, shape (B1, B2).
    """
    S = C_ab.copy()

    # For each criterion, apply the discordance reduction
    n_criteria = d_j.shape[2]
    for j in range(n_criteria):
        d = d_j[:, :, j]

        # Full veto (d=1) always sets S=0
        S[d >= 1.0] = 0.0

        # Where d > C and d < 1: multiply by (1-d)/(1-C)
        mask = (d > C_ab) & (d < 1.0)
        if mask.any():
            denom = 1.0 - C_ab[mask]
            denom = np.where(denom == 0, 1e-10, denom)
            factor = (1.0 - d[mask]) / denom
            S[mask] *= np.clip(factor, 0.0, 1.0)

    return np.clip(S, 0.0, 1.0)
