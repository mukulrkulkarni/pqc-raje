"""Discordance computation for ELECTRE III."""

import numpy as np


def discordance(
    diff: np.ndarray, p: np.ndarray, v: np.ndarray
) -> np.ndarray:
    """Compute discordance d_j(a,b) for each criterion.

    Formula:
        d_j(a,b) = 0           if g_j(a) - g_j(b) >= -p_j
        d_j(a,b) = 1           if g_j(a) - g_j(b) <= -v_j
        d_j(a,b) = linear      otherwise (interpolate between 0 and 1)

    The discordance measures how strongly criterion j opposes
    the assertion "a outranks b".

    Args:
        diff: Performance differences g(a) - g(b), shape (B1, B2, C).
        p: Preference thresholds, shape (C,).
        v: Veto thresholds, shape (C,).

    Returns:
        Discordance values, shape (B1, B2, C).
    """
    # Compute full interpolated values first for correct broadcasting
    denom = v - p
    denom = np.where(denom == 0, 1.0, denom)
    d_interp = (-diff - p) / denom

    # Apply conditions: veto checked first, then no-discordance, then interpolate
    d = np.where(diff <= -v, 1.0, np.where(diff >= -p, 0.0, d_interp))
    return np.clip(d, 0.0, 1.0)
