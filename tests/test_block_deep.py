"""block.py deep tutorial: executable contracts + invariants.

This file focuses on the composition contract of compute_block:
- output shape is (B1,B2)
- all values are in [0,1]
- diagonal clearing only when is_diagonal=True
- diagonal clearing affects the local diagonal only (min(B1,B2))
- off-diagonal blocks must NOT be zeroed by accident
"""

from __future__ import annotations

import numpy as np
import pytest

from electre3.block import compute_block


def _arrays(C: int):
    q = np.ones(C)
    p = np.full(C, 3.0)
    v = np.full(C, 6.0)
    w = np.full(C, 1.0 / C)
    return q, p, v, w


def test_shape_contract_rectangular_block() -> None:
    G_rows = np.arange(6.0).reshape(3, 2)
    G_cols = np.arange(8.0).reshape(4, 2)
    q, p, v, w = _arrays(2)
    S = compute_block(G_rows, G_cols, q, p, v, w, is_diagonal=False)
    assert S.shape == (3, 4)


def test_values_are_clipped_to_unit_interval() -> None:
    # Random values should not escape [0,1] if upstream modules behave.
    rng = np.random.default_rng(0)
    G_rows = rng.normal(size=(5, 3))
    G_cols = rng.normal(size=(7, 3))
    q, p, v, w = _arrays(3)
    S = compute_block(G_rows, G_cols, q, p, v, w, is_diagonal=False)
    assert np.all(S >= 0.0)
    assert np.all(S <= 1.0)


def test_diagonal_cleared_only_when_flag_true() -> None:
    # Identical rows/cols: without diagonal clearing, S(a,a)=1.
    G = np.array([[1.0, 1.0], [1.0, 1.0]])
    q, p, v, w = _arrays(2)

    S_off = compute_block(G, G, q, p, v, w, is_diagonal=False)
    np.testing.assert_allclose(np.diag(S_off), 1.0)

    S_diag = compute_block(G, G, q, p, v, w, is_diagonal=True)
    np.testing.assert_allclose(np.diag(S_diag), 0.0)


def test_local_diagonal_is_not_global_diagonal_in_offdiagonal_blocks() -> None:
    # Distinct alternatives can be identical. Off-diagonal blocks must not zero local diagonal.
    rows = np.array([[1.0, 1.0], [2.0, 2.0]])
    cols = np.array([[1.0, 1.0], [2.0, 2.0]])
    q, p, v, w = _arrays(2)

    S = compute_block(rows, cols, q, p, v, w, is_diagonal=False)
    # Both positions represent (a_i, b_i) for i=0,1, not self-comparisons.
    assert S[0, 0] == 1.0
    assert S[1, 1] == 1.0


def test_fill_diagonal_zeros_only_min_dimension() -> None:
    # Fill-diagonal zeros the first min(B1,B2) diagonal entries.
    rows = np.ones((2, 2))
    cols = np.ones((3, 2))
    q, p, v, w = _arrays(2)

    S = compute_block(rows, cols, q, p, v, w, is_diagonal=True)
    assert S.shape == (2, 3)
    assert S[0, 0] == 0.0
    assert S[1, 1] == 0.0
    # This is not on the local diagonal; must remain 1.
    assert S[0, 1] == 1.0
