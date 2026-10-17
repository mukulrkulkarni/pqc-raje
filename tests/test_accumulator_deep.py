"""accumulator.py deep tutorial: executable contracts + invariants.

This test suite verifies the *composition contract* of NetFlowAccumulator:
- update() maps block entries to the correct global indices via row_start/col_start
- accumulating blocks equals accumulating the full matrix when tiling is correct
- outflow.sum() == inflow.sum() holds for any updates (per-block invariance)
- normalize() contract for all-equal and non-degenerate cases

The accumulator deliberately does not validate bounds; a bad caller can trigger
IndexError or broadcasting errors.
"""

from __future__ import annotations

import numpy as np
import pytest

from electre3.accumulator import NetFlowAccumulator


def test_update_maps_row_and_col_sums_to_global_indices() -> None:
    """Asymmetric oracle: swapping row_start/col_start breaks this."""
    acc = NetFlowAccumulator(5)

    # Block covers global rows [1,2] and cols [3,4]
    S_block = np.array(
        [
            [1.0, 2.0],
            [3.0, 4.0],
        ],
        dtype=np.float64,
    )
    acc.update(S_block, row_start=1, col_start=3)

    # Row sums to outflow[1], outflow[2]
    assert np.allclose(acc.outflow, np.array([0.0, 3.0, 7.0, 0.0, 0.0]))
    # Col sums to inflow[3], inflow[4]
    assert np.allclose(acc.inflow, np.array([0.0, 0.0, 0.0, 4.0, 6.0]))
    assert acc.blocks_done == 1


def test_accumulating_selected_blocks_matches_manual_row_col_sums() -> None:
    """Accumulate two off-diagonal quadrants and compare with manual sums."""
    S = np.array(
        [
            [0.0, 0.1, 0.2, 0.3],
            [0.4, 0.0, 0.5, 0.6],
            [0.7, 0.8, 0.0, 0.9],
            [1.0, 1.1, 1.2, 0.0],
        ],
        dtype=np.float64,
    )

    acc = NetFlowAccumulator(4)

    # Tile into two blocks: rows 0..1 x cols 2..3, and rows 2..3 x cols 0..1
    acc.update(S[0:2, 2:4], row_start=0, col_start=2)
    acc.update(S[2:4, 0:2], row_start=2, col_start=0)

    # These blocks cover only off-diagonal entries included above.
    expected_outflow = np.array(
        [S[0, 2] + S[0, 3], S[1, 2] + S[1, 3], S[2, 0] + S[2, 1], S[3, 0] + S[3, 1]],
        dtype=np.float64,
    )
    expected_inflow = np.array(
        [S[2, 0] + S[3, 0], S[2, 1] + S[3, 1], S[0, 2] + S[1, 2], S[0, 3] + S[1, 3]],
        dtype=np.float64,
    )

    assert np.allclose(acc.outflow, expected_outflow)
    assert np.allclose(acc.inflow, expected_inflow)


def test_outflow_sum_equals_inflow_sum_for_any_updates() -> None:
    """Mass conservation holds per update, independent of tiling correctness."""
    acc = NetFlowAccumulator(5)

    # Two arbitrary blocks; conservation should still hold.
    acc.update(np.array([[1.0, 2.0], [3.0, 4.0]]), row_start=0, col_start=0)
    acc.update(np.array([[5.0]]), row_start=4, col_start=2)

    assert np.allclose(acc.outflow.sum(), acc.inflow.sum())


def test_net_flow_matches_full_definition() -> None:
    N = 4
    S = np.array(
        [
            [0.0, 0.2, 0.0, 0.9],
            [0.1, 0.0, 0.4, 0.0],
            [0.7, 0.0, 0.0, 0.3],
            [0.0, 0.6, 0.8, 0.0],
        ],
        dtype=np.float64,
    )
    acc = NetFlowAccumulator(N)
    acc.update(S, 0, 0)

    expected_out = S.sum(axis=1)
    expected_in = S.sum(axis=0)
    assert np.allclose(acc.outflow, expected_out)
    assert np.allclose(acc.inflow, expected_in)
    assert np.allclose(acc.net_flow(), expected_out - expected_in)


def test_normalize_all_equal_returns_half() -> None:
    acc = NetFlowAccumulator(3)
    # No updates: net_flow is [0,0,0]
    norm = acc.normalize()
    assert np.allclose(norm, np.array([0.5, 0.5, 0.5]))


def test_normalize_is_minmax_scaled_when_not_degenerate() -> None:
    acc = NetFlowAccumulator(3)
    acc.outflow[:] = np.array([1.0, 3.0, 2.0])
    acc.inflow[:] = 0.0
    norm = acc.normalize()
    assert np.allclose(norm.min(), 0.0)
    assert np.allclose(norm.max(), 1.0)


def test_bad_bounds_can_raise_from_numpy_broadcasting() -> None:
    acc = NetFlowAccumulator(3)
    S_block = np.ones((2, 2))

    # Row slice has length 1 but sum has length 2.
    with pytest.raises(ValueError):
        acc.update(S_block, row_start=2, col_start=0)

    # Col slice has length 1 but sum has length 2.
    with pytest.raises(ValueError):
        acc.update(S_block, row_start=0, col_start=2)


def test_negative_start_indices_can_silently_do_nothing_or_wrong_thing() -> None:
    """Negative starts rely on NumPy slicing semantics; caller must forbid them."""
    acc = NetFlowAccumulator(3)
    S_block = np.ones((1, 1))

    acc.update(S_block, row_start=-1, col_start=0)

    # For this shape, row slice [-1:0] is empty, so outflow is unchanged.
    # This kind of behaviour is a caller bug, not an accumulator guarantee.
    assert np.allclose(acc.outflow, np.zeros(3))
    assert np.allclose(acc.inflow, np.array([1.0, 0.0, 0.0]))
