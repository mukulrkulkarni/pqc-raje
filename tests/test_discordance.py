"""Tests for electre3.discordance module."""

import numpy as np
import pytest
from electre3.discordance import discordance


class TestDiscordance:
    """Tests for discordance computation."""

    def test_no_discordance(self):
        """Difference >= -p should give d=0."""
        diff = np.array([[[0.0]]])  # a equal to b
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 0.0

    def test_full_discordance(self):
        """Difference <= -v should give d=1 (veto)."""
        diff = np.array([[[-15.0]]])  # a much worse than b
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 1.0

    def test_interpolation(self):
        """Difference between -v and -p should interpolate."""
        diff = np.array([[[-7.5]]])  # between -10 and -5
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        # d = (-(-7.5) - 5) / (10 - 5) = (7.5 - 5) / 5 = 0.5
        assert abs(d[0, 0, 0] - 0.5) < 1e-10

    def test_boundary_at_minus_p(self):
        """Difference exactly at -p should give d=0."""
        diff = np.array([[[-5.0]]])
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 0.0

    def test_boundary_at_minus_v(self):
        """Difference exactly at -v should give d=1."""
        diff = np.array([[[-10.0]]])
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 1.0

    def test_multiple_criteria(self):
        """Should work with multiple criteria."""
        diff = np.array([[[0.0, -7.5, -15.0]]])
        p = np.array([5.0, 5.0, 5.0])
        v = np.array([10.0, 10.0, 10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 0.0  # No discordance
        assert abs(d[0, 0, 1] - 0.5) < 1e-10  # Interpolated
        assert d[0, 0, 2] == 1.0  # Full veto

    def test_block_shape(self):
        """Should handle block shapes correctly."""
        diff = np.random.randn(3, 4, 5)
        p = np.ones(5) * 2
        v = np.ones(5) * 5
        d = discordance(diff, p, v)
        assert d.shape == (3, 4, 5)

    def test_positive_diff(self):
        """Positive differences (a better than b) should give d=0."""
        diff = np.array([[[10.0]]])
        p = np.array([5.0])
        v = np.array([10.0])
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 0.0

    def test_equal_thresholds(self):
        """Should handle p == v edge case."""
        diff = np.array([[[-5.0]]])
        p = np.array([5.0])
        v = np.array([5.0])  # p == v
        d = discordance(diff, p, v)
        assert d[0, 0, 0] == 1.0  # At boundary, full discordance

    def test_values_in_range(self):
        """Discordance values should be in [0, 1]."""
        diff = np.random.randn(10, 10, 5) * 20
        p = np.ones(5) * 3
        v = np.ones(5) * 8
        d = discordance(diff, p, v)
        assert d.min() >= 0.0
        assert d.max() <= 1.0
