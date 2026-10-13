"""Tests for electre3.accumulator module."""

import numpy as np
import pytest
from electre3.accumulator import NetFlowAccumulator


class TestNetFlowAccumulator:
    """Tests for NetFlowAccumulator class."""

    def test_init(self):
        """Accumulator should initialize with zeros."""
        acc = NetFlowAccumulator(5)
        assert acc.n_alternatives == 5
        assert np.allclose(acc.outflow, 0)
        assert np.allclose(acc.inflow, 0)
        assert acc.blocks_done == 0

    def test_single_block_update(self):
        """Single block update should set outflow and inflow correctly."""
        acc = NetFlowAccumulator(3)
        S_block = np.array([
            [0.0, 0.8, 0.6],
            [0.2, 0.0, 0.7],
            [0.4, 0.3, 0.0],
        ])
        acc.update(S_block, 0, 0)

        # Outflow: row sums
        expected_outflow = [0.8 + 0.6, 0.2 + 0.7, 0.4 + 0.3]
        assert np.allclose(acc.outflow, expected_outflow)

        # Inflow: column sums
        expected_inflow = [0.2 + 0.4, 0.8 + 0.3, 0.6 + 0.7]
        assert np.allclose(acc.inflow, expected_inflow)

        assert acc.blocks_done == 1

    def test_multiple_block_updates(self):
        """Multiple block updates should accumulate."""
        acc = NetFlowAccumulator(4)

        # First block: rows 0-1, cols 0-1
        S1 = np.array([[0.0, 0.5], [0.3, 0.0]])
        acc.update(S1, 0, 0)

        # Second block: rows 0-1, cols 2-3
        S2 = np.array([[0.7, 0.4], [0.2, 0.6]])
        acc.update(S2, 0, 2)

        # Outflow for rows 0-1 should accumulate
        assert acc.outflow[0] == 0.5 + 0.7 + 0.4
        assert acc.outflow[1] == 0.3 + 0.2 + 0.6
        assert acc.blocks_done == 2

    def test_net_flow(self):
        """Net flow should be outflow minus inflow."""
        acc = NetFlowAccumulator(3)
        acc.outflow = np.array([1.5, 0.8, 1.2])
        acc.inflow = np.array([0.9, 1.4, 1.2])

        net = acc.net_flow()
        expected = [0.6, -0.6, 0.0]
        assert np.allclose(net, expected)

    def test_normalize_basic(self):
        """Normalize should scale to [0, 1]."""
        acc = NetFlowAccumulator(3)
        acc.outflow = np.array([2.0, 1.0, 0.5])
        acc.inflow = np.array([0.5, 1.0, 2.0])
        # net_flow = [1.5, 0.0, -1.5]

        norm = acc.normalize()
        assert norm.min() == 0.0
        assert norm.max() == 1.0
        assert abs(norm[1] - 0.5) < 1e-10  # Middle value

    def test_normalize_all_equal(self):
        """When all equal, normalize should return 0.5."""
        acc = NetFlowAccumulator(3)
        acc.outflow = np.array([1.0, 1.0, 1.0])
        acc.inflow = np.array([1.0, 1.0, 1.0])

        norm = acc.normalize()
        assert np.allclose(norm, 0.5)

    def test_block_offset(self):
        """Updates with different offsets should go to correct positions."""
        acc = NetFlowAccumulator(6)

        # Block in middle of matrix
        S_block = np.array([[0.5, 0.6], [0.7, 0.8]])
        acc.update(S_block, 2, 3)

        # Only rows 2-3 should have outflow
        assert acc.outflow[0] == 0.0
        assert acc.outflow[1] == 0.0
        assert acc.outflow[2] == 0.5 + 0.6
        assert acc.outflow[3] == 0.7 + 0.8
        assert acc.outflow[4] == 0.0

        # Only cols 3-4 should have inflow
        assert acc.inflow[2] == 0.0
        assert acc.inflow[3] == 0.5 + 0.7
        assert acc.inflow[4] == 0.6 + 0.8

    def test_asymmetric_block(self):
        """Should handle non-square blocks."""
        acc = NetFlowAccumulator(5)
        S_block = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ])
        acc.update(S_block, 1, 2)

        assert acc.outflow[1] == 0.1 + 0.2 + 0.3
        assert acc.outflow[2] == 0.4 + 0.5 + 0.6
        assert acc.inflow[2] == 0.1 + 0.4
        assert acc.inflow[3] == 0.2 + 0.5
        assert acc.inflow[4] == 0.3 + 0.6

    def test_deterministic_accumulation(self):
        """Same updates should give same results."""
        acc1 = NetFlowAccumulator(4)
        acc2 = NetFlowAccumulator(4)

        blocks = [
            (np.random.rand(2, 2), 0, 0),
            (np.random.rand(2, 2), 0, 2),
            (np.random.rand(2, 2), 2, 0),
            (np.random.rand(2, 2), 2, 2),
        ]

        for S, rs, cs in blocks:
            acc1.update(S, rs, cs)
            acc2.update(S, rs, cs)

        assert np.allclose(acc1.net_flow(), acc2.net_flow())
