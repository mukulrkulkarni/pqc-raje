"""Tests for electre3.concordance module."""

import numpy as np
import pytest
from electre3.concordance import partial_concordance, global_concordance


class TestPartialConcordance:
    """Tests for partial concordance computation."""

    def test_full_concordance(self):
        """Difference >= -q should give c=1."""
        diff = np.array([[[5.0]]])  # a much better than b
        q = np.array([3.0])
        p = np.array([5.0])
        c = partial_concordance(diff, q, p)
        assert c[0, 0, 0] == 1.0

    def test_zero_concordance(self):
        """Difference <= -p should give c=0."""
        diff = np.array([[[-10.0]]])  # a much worse than b
        q = np.array([3.0])
        p = np.array([5.0])
        c = partial_concordance(diff, q, p)
        assert c[0, 0, 0] == 0.0

    def test_interpolation(self):
        """Difference between -p and -q should interpolate."""
        diff = np.array([[[-4.0]]])  # between -5 and -3
        q = np.array([3.0])
        p = np.array([5.0])
        c = partial_concordance(diff, q, p)
        # c = (-4 + 5) / (5 - 3) = 1/2 = 0.5
        assert abs(c[0, 0, 0] - 0.5) < 1e-10

    def test_boundary_at_minus_q(self):
        """Difference exactly at -q should give c=1."""
        diff = np.array([[[-3.0]]])
        q = np.array([3.0])
        p = np.array([5.0])
        c = partial_concordance(diff, q, p)
        assert c[0, 0, 0] == 1.0

    def test_boundary_at_minus_p(self):
        """Difference exactly at -p should give c=0."""
        diff = np.array([[[-5.0]]])
        q = np.array([3.0])
        p = np.array([5.0])
        c = partial_concordance(diff, q, p)
        assert c[0, 0, 0] == 0.0

    def test_multiple_criteria(self):
        """Should work with multiple criteria."""
        diff = np.array([[[5.0, -4.0, -10.0]]])
        q = np.array([3.0, 3.0, 3.0])
        p = np.array([5.0, 5.0, 5.0])
        c = partial_concordance(diff, q, p)
        assert c[0, 0, 0] == 1.0  # Full
        assert abs(c[0, 0, 1] - 0.5) < 1e-10  # Interpolated
        assert c[0, 0, 2] == 0.0  # Zero

    def test_block_shape(self):
        """Should handle block shapes correctly."""
        diff = np.random.randn(3, 4, 5)
        q = np.ones(5)
        p = np.ones(5) * 2
        c = partial_concordance(diff, q, p)
        assert c.shape == (3, 4, 5)

    def test_equal_thresholds(self):
        """Should handle q == p edge case."""
        diff = np.array([[[-3.0]]])
        q = np.array([3.0])
        p = np.array([3.0])  # q == p
        c = partial_concordance(diff, q, p)
        # Should be 1 since diff >= -q
        assert c[0, 0, 0] == 1.0


class TestGlobalConcordance:
    """Tests for global concordance computation."""

    def test_weighted_sum(self):
        """Global concordance is weighted sum of partial concordances."""
        c_j = np.array([[[1.0, 0.5, 0.0]]])
        weights = np.array([0.5, 0.3, 0.2])
        C = global_concordance(c_j, weights)
        expected = 0.5 * 1.0 + 0.3 * 0.5 + 0.2 * 0.0
        assert abs(C[0, 0] - expected) < 1e-10

    def test_uniform_weights(self):
        """Uniform weights should give simple average."""
        c_j = np.array([[[0.8, 0.6, 0.4]]])
        weights = np.array([1/3, 1/3, 1/3])
        C = global_concordance(c_j, weights)
        expected = (0.8 + 0.6 + 0.4) / 3
        assert abs(C[0, 0] - expected) < 1e-10

    def test_single_criterion(self):
        """Single criterion should equal that criterion's concordance."""
        c_j = np.array([[[0.75]]])
        weights = np.array([1.0])
        C = global_concordance(c_j, weights)
        assert C[0, 0] == 0.75

    def test_block_shape(self):
        """Should output correct shape."""
        c_j = np.random.rand(3, 4, 5)
        weights = np.ones(5) / 5
        C = global_concordance(c_j, weights)
        assert C.shape == (3, 4)

    def test_all_ones(self):
        """All c_j=1 should give C=1."""
        c_j = np.ones((2, 3, 4))
        weights = np.array([0.1, 0.2, 0.3, 0.4])
        C = global_concordance(c_j, weights)
        assert np.allclose(C, 1.0)

    def test_all_zeros(self):
        """All c_j=0 should give C=0."""
        c_j = np.zeros((2, 3, 4))
        weights = np.array([0.1, 0.2, 0.3, 0.4])
        C = global_concordance(c_j, weights)
        assert np.allclose(C, 0.0)
