"""Block computation for ELECTRE III credibility matrix."""

import numpy as np

from .concordance import partial_concordance, global_concordance
from .discordance import discordance
from .credibility import credibility


def compute_block(
    G_rows: np.ndarray,
    G_cols: np.ndarray,
    q: np.ndarray,
    p: np.ndarray,
    v: np.ndarray,
    weights: np.ndarray,
    is_diagonal: bool = False,
) -> np.ndarray:
    """Compute credibility S(a,b) for one block of alternatives.

    Args:
        G_rows: Performance matrix rows for alternatives a, shape (B1, C).
        G_cols: Performance matrix rows for alternatives b, shape (B2, C).
        q: Indifference thresholds, shape (C,).
        p: Preference thresholds, shape (C,).
        v: Veto thresholds, shape (C,).
        weights: Normalized criterion weights, shape (C,).
        is_diagonal: True if this is a diagonal block (same alternatives).

    Returns:
        Credibility values S(a,b), shape (B1, B2).
    """
    # Compute differences: diff[i,j,k] = G_rows[i,k] - G_cols[j,k]
    diff = G_rows[:, np.newaxis, :] - G_cols[np.newaxis, :, :]

    # Concordance
    c_j = partial_concordance(diff, q, p)
    C_ab = global_concordance(c_j, weights)

    # Discordance
    d_j = discordance(diff, p, v)

    # Credibility
    S = credibility(C_ab, d_j)

    # Diagonal: S(a,a) = 0
    if is_diagonal:
        np.fill_diagonal(S, 0.0)

    return S
