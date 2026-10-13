"""Concordance computation for ELECTRE III."""

import numpy as np


def partial_concordance(
    diff: np.ndarray, q: np.ndarray, p: np.ndarray
) -> np.ndarray:
    """Compute partial concordance c_j(a,b) for each criterion.

    Formula:
        c_j(a,b) = 1           if g_j(a) - g_j(b) >= -q_j
        c_j(a,b) = 0           if g_j(a) - g_j(b) <= -p_j
        c_j(a,b) = linear      otherwise (interpolate between 0 and 1)

    Args:
        diff: Performance differences g(a) - g(b), shape (B1, B2, C).
        q: Indifference thresholds, shape (C,).
        p: Preference thresholds, shape (C,).

    Returns:
        Partial concordance values, shape (B1, B2, C).
    """
    # Compute full interpolated values first for correct broadcasting
    denom = p - q
    denom = np.where(denom == 0, 1.0, denom)
    c_interp = (diff + p) / denom

    # Apply conditions
    c = np.where(diff >= -q, 1.0, np.where(diff <= -p, 0.0, c_interp))
    return np.clip(c, 0.0, 1.0)


def global_concordance(c_j: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Compute global concordance C(a,b) as weighted sum.

    Formula:
        C(a,b) = Σ w_j * c_j(a,b)

    Args:
        c_j: Partial concordance values, shape (B1, B2, C).
        weights: Normalized weights, shape (C,).

    Returns:
        Global concordance values, shape (B1, B2).
    """
    return np.einsum("ijk,k->ij", c_j, weights)
