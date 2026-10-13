"""Tests for electre3.credibility module."""

import numpy as np
import pytest
from electre3.credibility import credibility


class TestCredibility:
    """Tests for credibility computation."""

    def test_no_discordance(self):
        """When all d <= C, S = C."""
        C_ab = np.array([[0.8]])
        d_j = np.array([[[0.5, 0.3, 0.2]]])  # All <= 0.8
        S = credibility(C_ab, d_j)
        assert S[0, 0] == 0.8

    def test_single_veto(self):
        """Single d > C should reduce S."""
        C_ab = np.array([[0.8]])
        d_j = np.array([[[0.5, 0.9, 0.2]]])  # d[1] = 0.9 > C = 0.8
        S = credibility(C_ab, d_j)
        # S = 0.8 * (1-0.9)/(1-0.8) = 0.8 * 0.1/0.2 = 0.8 * 0.5 = 0.4
        assert abs(S[0, 0] - 0.4) < 1e-10

    def test_full_veto(self):
        """d = 1 should give S = 0."""
        C_ab = np.array([[0.8]])
        d_j = np.array([[[0.5, 1.0, 0.2]]])  # d[1] = 1.0 (veto)
        S = credibility(C_ab, d_j)
        assert S[0, 0] == 0.0

    def test_multiple_discordances(self):
        """Multiple d > C should compound."""
        C_ab = np.array([[0.6]])
        d_j = np.array([[[0.7, 0.8]]])  # Both > 0.6
        S = credibility(C_ab, d_j)
        # Factor for d[0]: (1-0.7)/(1-0.6) = 0.3/0.4 = 0.75
        # Factor for d[1]: (1-0.8)/(1-0.6) = 0.2/0.4 = 0.5
        # S = 0.6 * 0.75 * 0.5 = 0.225
        assert abs(S[0, 0] - 0.225) < 1e-10

    def test_perfect_concordance_no_veto(self):
        """C = 1 with all d < 1 should give S = 1."""
        C_ab = np.array([[1.0]])
        d_j = np.array([[[0.5, 0.9, 0.3]]])  # None = 1
        S = credibility(C_ab, d_j)
        assert S[0, 0] == 1.0

    def test_perfect_concordance_with_veto(self):
        """C = 1 with d = 1 should give S = 0."""
        C_ab = np.array([[1.0]])
        d_j = np.array([[[0.5, 1.0, 0.3]]])  # d[1] = 1.0
        S = credibility(C_ab, d_j)
        assert S[0, 0] == 0.0

    def test_zero_concordance(self):
        """C = 0 should give S = 0."""
        C_ab = np.array([[0.0]])
        d_j = np.array([[[0.5, 0.3, 0.2]]])
        S = credibility(C_ab, d_j)
        assert S[0, 0] == 0.0

    def test_block_shape(self):
        """Should output correct shape."""
        C_ab = np.random.rand(3, 4)
        d_j = np.random.rand(3, 4, 5)
        S = credibility(C_ab, d_j)
        assert S.shape == (3, 4)

    def test_values_in_range(self):
        """Credibility values should be in [0, 1]."""
        C_ab = np.random.rand(10, 10)
        d_j = np.random.rand(10, 10, 5)
        S = credibility(C_ab, d_j)
        assert S.min() >= 0.0
        assert S.max() <= 1.0

    def test_symmetric_input(self):
        """Symmetric inputs should produce consistent results."""
        C_ab = np.full((2, 2), 0.7)
        d_j = np.full((2, 2, 3), 0.5)
        S = credibility(C_ab, d_j)
        # All entries should be equal
        assert np.allclose(S, S[0, 0])
