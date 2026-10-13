"""Tests for electre3.validate module."""

import numpy as np
import pytest
from electre3.config import CriterionConfig
from electre3.validate import validate_thresholds, normalize_weights, validate_matrix


class TestValidateThresholds:
    """Tests for threshold validation."""

    def test_valid_thresholds(self):
        """Valid thresholds should not raise."""
        criteria = [
            CriterionConfig("A", weight=1, q=5, p=10, v=20),
            CriterionConfig("B", weight=1, q=0, p=5, v=10),
        ]
        validate_thresholds(criteria)  # Should not raise

    def test_negative_q(self):
        """Negative q should raise ValueError at config creation."""
        with pytest.raises(ValueError, match="q must be >= 0"):
            CriterionConfig("A", weight=1, q=-1, p=5, v=10)

    def test_p_less_than_q(self):
        """p < q should raise ValueError at config creation."""
        with pytest.raises(ValueError, match="p must be >= q"):
            CriterionConfig("A", weight=1, q=10, p=5, v=20)

    def test_v_less_than_p(self):
        """v < p should raise ValueError at config creation."""
        with pytest.raises(ValueError, match="v must be >= p"):
            CriterionConfig("A", weight=1, q=5, p=15, v=10)

    def test_equal_thresholds_valid(self):
        """Equal thresholds (q=p=v) should be valid."""
        criteria = [CriterionConfig("A", weight=1, q=5, p=5, v=5)]
        validate_thresholds(criteria)  # Should not raise


class TestNormalizeWeights:
    """Tests for weight normalization."""

    def test_normalizes_to_one(self):
        """Normalized weights should sum to 1."""
        criteria = [
            CriterionConfig("A", weight=2, q=1, p=2, v=3),
            CriterionConfig("B", weight=3, q=1, p=2, v=3),
        ]
        weights = normalize_weights(criteria)
        assert abs(weights.sum() - 1.0) < 1e-10

    def test_preserves_ratios(self):
        """Should preserve weight ratios."""
        criteria = [
            CriterionConfig("A", weight=1, q=1, p=2, v=3),
            CriterionConfig("B", weight=2, q=1, p=2, v=3),
        ]
        weights = normalize_weights(criteria)
        assert abs(weights[1] / weights[0] - 2.0) < 1e-10

    def test_returns_ndarray(self):
        """Should return numpy array."""
        criteria = [CriterionConfig("A", weight=1, q=1, p=2, v=3)]
        weights = normalize_weights(criteria)
        assert isinstance(weights, np.ndarray)

    def test_float64_dtype(self):
        """Should return float64."""
        criteria = [CriterionConfig("A", weight=1, q=1, p=2, v=3)]
        weights = normalize_weights(criteria)
        assert weights.dtype == np.float64


class TestValidateMatrix:
    """Tests for matrix validation."""

    def test_valid_matrix(self):
        """Valid matrix should not raise."""
        G = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        validate_matrix(G, 2)  # Should not raise

    def test_wrong_dimensions(self):
        """1D matrix should raise ValueError."""
        G = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="must be 2D"):
            validate_matrix(G, 3)

    def test_too_few_alternatives(self):
        """Single alternative should raise ValueError."""
        G = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="at least 2 alternatives"):
            validate_matrix(G, 2)

    def test_wrong_criteria_count(self):
        """Mismatched criteria count should raise ValueError."""
        G = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError, match="expected 3"):
            validate_matrix(G, 3)

    def test_contains_nan(self):
        """Matrix with NaN should raise ValueError."""
        G = np.array([[1.0, np.nan], [3.0, 4.0]])
        with pytest.raises(ValueError, match="NaN"):
            validate_matrix(G, 2)

    def test_contains_inf(self):
        """Matrix with inf should raise ValueError."""
        G = np.array([[1.0, np.inf], [3.0, 4.0]])
        with pytest.raises(ValueError, match="infinite"):
            validate_matrix(G, 2)

    def test_contains_negative_inf(self):
        """Matrix with -inf should raise ValueError."""
        G = np.array([[1.0, -np.inf], [3.0, 4.0]])
        with pytest.raises(ValueError, match="infinite"):
            validate_matrix(G, 2)

    def test_large_matrix(self):
        """Large matrix should be valid."""
        G = np.random.rand(1000, 10)
        validate_matrix(G, 10)  # Should not raise

    def test_negative_values_valid(self):
        """Negative values should be valid."""
        G = np.array([[-1.0, -2.0], [-3.0, -4.0]])
        validate_matrix(G, 2)  # Should not raise
