"""Tests for electre3.config module."""

import pytest
from electre3.config import CriterionConfig, ComputeConfig, normalize_weights


class TestCriterionConfig:
    """Tests for CriterionConfig dataclass."""

    def test_valid_config(self):
        """Valid configuration should not raise."""
        cfg = CriterionConfig("Price", weight=1.0, q=5, p=10, v=20)
        assert cfg.name == "Price"
        assert cfg.weight == 1.0
        assert cfg.q == 5
        assert cfg.p == 10
        assert cfg.v == 20
        assert cfg.maximize is True

    def test_minimize_criterion(self):
        """Can create cost criterion with maximize=False."""
        cfg = CriterionConfig("Cost", weight=1.0, q=1, p=2, v=3, maximize=False)
        assert cfg.maximize is False

    def test_invalid_q_negative(self):
        """Negative q should raise ValueError."""
        with pytest.raises(ValueError, match="q must be >= 0"):
            CriterionConfig("X", weight=1, q=-1, p=5, v=10)

    def test_invalid_p_less_than_q(self):
        """p < q should raise ValueError."""
        with pytest.raises(ValueError, match="p must be >= q"):
            CriterionConfig("X", weight=1, q=10, p=5, v=20)

    def test_invalid_v_less_than_p(self):
        """v < p should raise ValueError."""
        with pytest.raises(ValueError, match="v must be >= p"):
            CriterionConfig("X", weight=1, q=5, p=15, v=10)

    def test_invalid_zero_weight(self):
        """Zero weight should raise ValueError."""
        with pytest.raises(ValueError, match="weight must be > 0"):
            CriterionConfig("X", weight=0, q=1, p=2, v=3)

    def test_invalid_negative_weight(self):
        """Negative weight should raise ValueError."""
        with pytest.raises(ValueError, match="weight must be > 0"):
            CriterionConfig("X", weight=-1, q=1, p=2, v=3)

    def test_edge_case_equal_thresholds(self):
        """q == p == v is valid."""
        cfg = CriterionConfig("X", weight=1, q=5, p=5, v=5)
        assert cfg.q == cfg.p == cfg.v == 5


class TestComputeConfig:
    """Tests for ComputeConfig dataclass."""

    def test_default_values(self):
        """Default configuration should work."""
        cfg = ComputeConfig()
        assert cfg.block_size == 1000
        assert cfg.use_numba is True
        assert cfg.seed is None

    def test_custom_block_size(self):
        """Custom block size should be accepted."""
        cfg = ComputeConfig(block_size=500)
        assert cfg.block_size == 500

    def test_invalid_zero_block_size(self):
        """Zero block size should raise ValueError."""
        with pytest.raises(ValueError, match="block_size must be >= 1"):
            ComputeConfig(block_size=0)

    def test_invalid_negative_block_size(self):
        """Negative block size should raise ValueError."""
        with pytest.raises(ValueError, match="block_size must be >= 1"):
            ComputeConfig(block_size=-100)

    def test_with_seed(self):
        """Seed can be set for reproducibility."""
        cfg = ComputeConfig(seed=42)
        assert cfg.seed == 42


class TestNormalizeWeights:
    """Tests for normalize_weights function."""

    def test_normalizes_to_one(self):
        """Normalized weights should sum to 1.0."""
        criteria = [
            CriterionConfig("A", weight=3, q=1, p=2, v=3),
            CriterionConfig("B", weight=2, q=1, p=2, v=3),
        ]
        weights = normalize_weights(criteria)
        assert len(weights) == 2
        assert abs(sum(weights) - 1.0) < 1e-10
        assert abs(weights[0] - 0.6) < 1e-10
        assert abs(weights[1] - 0.4) < 1e-10

    def test_single_criterion(self):
        """Single criterion should normalize to 1.0."""
        criteria = [CriterionConfig("A", weight=5, q=1, p=2, v=3)]
        weights = normalize_weights(criteria)
        assert weights == [1.0]

    def test_equal_weights(self):
        """Equal weights should normalize equally."""
        criteria = [
            CriterionConfig("A", weight=1, q=1, p=2, v=3),
            CriterionConfig("B", weight=1, q=1, p=2, v=3),
            CriterionConfig("C", weight=1, q=1, p=2, v=3),
        ]
        weights = normalize_weights(criteria)
        for w in weights:
            assert abs(w - 1/3) < 1e-10

    def test_preserves_order(self):
        """Weights should be in same order as criteria."""
        criteria = [
            CriterionConfig("First", weight=1, q=1, p=2, v=3),
            CriterionConfig("Second", weight=4, q=1, p=2, v=3),
        ]
        weights = normalize_weights(criteria)
        assert weights[0] < weights[1]
