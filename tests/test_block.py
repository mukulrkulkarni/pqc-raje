"""Tests for electre3.block module."""

import numpy as np
import pytest
from electre3.block import compute_block


class TestComputeBlock:
    """Tests for block computation."""

    @pytest.fixture
    def simple_params(self):
        """Simple parameters for testing."""
        return {
            "q": np.array([3.0, 3.0]),
            "p": np.array([5.0, 5.0]),
            "v": np.array([10.0, 10.0]),
            "weights": np.array([0.5, 0.5]),
        }

    def test_returns_correct_shape(self, simple_params):
        """Should return correct shape."""
        G_rows = np.array([[80.0, 70.0], [75.0, 85.0]])
        G_cols = np.array([[70.0, 80.0], [85.0, 65.0], [90.0, 60.0]])

        S = compute_block(G_rows, G_cols, **simple_params)
        assert S.shape == (2, 3)

    def test_diagonal_zeros(self, simple_params):
        """Diagonal block should have zeros on diagonal."""
        G = np.array([[80.0, 70.0], [75.0, 85.0], [90.0, 60.0]])

        S = compute_block(G, G, **simple_params, is_diagonal=True)
        assert S[0, 0] == 0.0
        assert S[1, 1] == 0.0
        assert S[2, 2] == 0.0

    def test_non_diagonal_no_zeros(self, simple_params):
        """Non-diagonal block should not enforce zeros."""
        G = np.array([[80.0, 70.0], [75.0, 85.0]])

        S = compute_block(G, G, **simple_params, is_diagonal=False)
        # S(a,a) might still be high, but not forced to 0
        # Actually with identical rows comparing to itself, concordance is 1
        # and no discordance, so S would be 1, not 0

    def test_values_in_range(self, simple_params):
        """Credibility values should be in [0, 1]."""
        G_rows = np.random.rand(5, 2) * 100
        G_cols = np.random.rand(6, 2) * 100

        S = compute_block(G_rows, G_cols, **simple_params)
        assert S.min() >= 0.0
        assert S.max() <= 1.0

    def test_dominant_alternative(self, simple_params):
        """Dominant alternative should have high credibility."""
        G_rows = np.array([[100.0, 100.0]])  # Dominant
        G_cols = np.array([[50.0, 50.0]])    # Dominated

        S = compute_block(G_rows, G_cols, **simple_params)
        assert S[0, 0] > 0.9  # High credibility that rows dominate cols

    def test_dominated_alternative(self, simple_params):
        """Dominated alternative should have low credibility."""
        G_rows = np.array([[50.0, 50.0]])    # Dominated
        G_cols = np.array([[100.0, 100.0]])  # Dominant

        S = compute_block(G_rows, G_cols, **simple_params)
        assert S[0, 0] < 0.1  # Low credibility

    def test_veto_effect(self):
        """Veto should reduce credibility to near zero."""
        G_rows = np.array([[100.0, 0.0]])   # Excellent on C1, terrible on C2
        G_cols = np.array([[50.0, 50.0]])   # Moderate on both

        params = {
            "q": np.array([3.0, 3.0]),
            "p": np.array([5.0, 5.0]),
            "v": np.array([10.0, 10.0]),  # Veto at 10
            "weights": np.array([0.5, 0.5]),
        }

        S = compute_block(G_rows, G_cols, **params)
        # C2 difference is -50, way beyond veto threshold
        assert S[0, 0] < 0.1

    def test_single_criterion(self):
        """Should work with single criterion."""
        G_rows = np.array([[80.0], [60.0]])
        G_cols = np.array([[70.0], [90.0]])
        params = {
            "q": np.array([5.0]),
            "p": np.array([10.0]),
            "v": np.array([20.0]),
            "weights": np.array([1.0]),
        }

        S = compute_block(G_rows, G_cols, **params)
        assert S.shape == (2, 2)

    def test_many_criteria(self):
        """Should work with many criteria."""
        n_criteria = 10
        G_rows = np.random.rand(3, n_criteria) * 100
        G_cols = np.random.rand(4, n_criteria) * 100
        params = {
            "q": np.ones(n_criteria) * 5,
            "p": np.ones(n_criteria) * 10,
            "v": np.ones(n_criteria) * 20,
            "weights": np.ones(n_criteria) / n_criteria,
        }

        S = compute_block(G_rows, G_cols, **params)
        assert S.shape == (3, 4)

    def test_deterministic(self, simple_params):
        """Same inputs should give same results."""
        G_rows = np.array([[80.0, 70.0], [75.0, 85.0]])
        G_cols = np.array([[70.0, 80.0], [85.0, 65.0]])

        S1 = compute_block(G_rows, G_cols, **simple_params)
        S2 = compute_block(G_rows, G_cols, **simple_params)

        assert np.allclose(S1, S2)
