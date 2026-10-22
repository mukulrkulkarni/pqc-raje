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
    directions: np.ndarray | None = None,
) -> np.ndarray:
    """Compute credibility ``S(a,b)`` for one block of alternatives.

    ``directions`` contains ``+1`` for maximize criteria and ``-1`` for minimize
    criteria. Applying it to raw pairwise differences preserves subnormal and ULP
    information that would be lost by materializing the semantic ``1 - g`` transform.
    """
    # diff[i, j, k] = g(a, k) - g(b, k). A minimize criterion needs g(b)-g(a).
    diff = G_rows[:, np.newaxis, :] - G_cols[np.newaxis, :, :]
    if directions is not None:
        directions = np.asarray(directions, dtype=np.float64)
        if directions.shape != (diff.shape[2],) or not np.all(np.isin(directions, (-1.0, 1.0))):
            raise ValueError("directions must contain one +1 or -1 value per criterion")
        diff *= directions

    c_j = partial_concordance(diff, q, p)
    C_ab = global_concordance(c_j, weights)
    d_j = discordance(diff, p, v)
    S = credibility(C_ab, d_j)

    if is_diagonal:
        np.fill_diagonal(S, 0.0)

    return S
