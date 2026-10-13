"""Negative tests for error handling and edge cases."""

import numpy as np
import pytest
from electre3.config import CriterionConfig, ComputeConfig
from electre3.ranking import compute_ranking
from electre3.validate import validate_matrix


class TestInvalidInputs:
    """Tests for handling invalid inputs."""

    def test_1d_matrix_rejected(self):
        """1D matrix should be rejected."""
        G = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="2D"):
            validate_matrix(G, 1)

    def test_3d_matrix_rejected(self):
        """3D matrix should be rejected."""
        G = np.ones((3, 3, 3))
        with pytest.raises(ValueError, match="2D"):
            validate_matrix(G, 3)

    def test_single_alternative_rejected(self):
        """Single alternative should be rejected."""
        G = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="at least 2"):
            validate_matrix(G, 2)

    def test_nan_in_matrix_rejected(self):
        """Matrix with NaN should be rejected."""
        G = np.array([[1.0, np.nan], [3.0, 4.0]])
        with pytest.raises(ValueError, match="NaN"):
            validate_matrix(G, 2)

    def test_inf_in_matrix_rejected(self):
        """Matrix with infinity should be rejected."""
        G = np.array([[1.0, np.inf], [3.0, 4.0]])
        with pytest.raises(ValueError, match="infinite"):
            validate_matrix(G, 2)

    def test_wrong_criterion_count(self):
        """Mismatched criterion count should be rejected."""
        G = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError, match="expected 5"):
            validate_matrix(G, 5)

    def test_zero_block_size_rejected(self):
        """Zero block size should be rejected."""
        with pytest.raises(ValueError, match="block_size"):
            ComputeConfig(block_size=0)

    def test_negative_block_size_rejected(self):
        """Negative block size should be rejected."""
        with pytest.raises(ValueError, match="block_size"):
            ComputeConfig(block_size=-10)


class TestEmptyCriteriaRejected:
    """Tests for empty criteria handling."""

    def test_compute_ranking_rejects_empty_criteria_valueerror(self):
        """compute_ranking must raise ValueError on empty criteria list."""
        G = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError, match="empty"):
            compute_ranking(G, [])


class TestArrayLengthMismatch:
    """Tests for threshold/weight array length mismatch."""

    def test_compute_block_rejects_threshold_length_mismatch(self):
        """Mismatched threshold arrays should raise ValueError."""
        from electre3.validate import validate_arrays_match
        q = np.array([0.1, 0.2])
        p = np.array([0.2, 0.3, 0.4])  # Wrong length
        v = np.array([0.5, 0.6])
        w = np.array([0.5, 0.5])
        with pytest.raises(ValueError, match="mismatch"):
            validate_arrays_match(q, p, v, w)

    def test_compute_block_rejects_weight_length_mismatch(self):
        """Mismatched weight array should raise ValueError."""
        from electre3.validate import validate_arrays_match
        q = np.array([0.1, 0.2])
        p = np.array([0.2, 0.3])
        v = np.array([0.5, 0.6])
        w = np.array([0.3, 0.3, 0.4])  # Wrong length
        with pytest.raises(ValueError, match="mismatch"):
            validate_arrays_match(q, p, v, w)


class TestNaNInfRejected:
    """Tests for NaN/Inf value rejection."""

    def test_criterion_config_rejects_nan_threshold(self):
        """CriterionConfig must reject NaN thresholds."""
        with pytest.raises(ValueError, match="finite"):
            CriterionConfig("test", weight=1.0, q=float('nan'), p=0.2, v=0.5)

    def test_criterion_config_rejects_inf_threshold(self):
        """CriterionConfig must reject infinite thresholds."""
        with pytest.raises(ValueError, match="finite"):
            CriterionConfig("test", weight=1.0, q=0.1, p=float('inf'), v=0.5)

    def test_criterion_config_rejects_nan_weight(self):
        """CriterionConfig must reject NaN weight."""
        with pytest.raises(ValueError, match="finite"):
            CriterionConfig("test", weight=float('nan'), q=0.1, p=0.2, v=0.5)

    def test_criterion_config_rejects_inf_weight(self):
        """CriterionConfig must reject infinite weight."""
        with pytest.raises(ValueError, match="finite"):
            CriterionConfig("test", weight=float('inf'), q=0.1, p=0.2, v=0.5)

    def test_normalize_weights_rejects_nan_weights(self):
        """normalize_weights must reject NaN in weights array."""
        from electre3.validate import normalize_weights
        criteria = [
            CriterionConfig("a", weight=1.0, q=0.1, p=0.2, v=0.5),
            CriterionConfig("b", weight=1.0, q=0.1, p=0.2, v=0.5),
        ]
        # Manually corrupt (bypass CriterionConfig check)
        criteria[0].weight = float('nan')
        with pytest.raises(ValueError, match="NaN"):
            normalize_weights(criteria)

    def test_normalize_weights_rejects_inf_weights(self):
        """normalize_weights must reject infinite weights."""
        from electre3.validate import normalize_weights
        criteria = [
            CriterionConfig("a", weight=1.0, q=0.1, p=0.2, v=0.5),
            CriterionConfig("b", weight=1.0, q=0.1, p=0.2, v=0.5),
        ]
        # Manually corrupt (bypass CriterionConfig check)
        criteria[0].weight = float('inf')
        with pytest.raises(ValueError, match="infinite"):
            normalize_weights(criteria)


class TestDiagonalZero:
    """Tests for diagonal being zero in credibility matrix."""

    def test_compute_block_diagonal_is_zero(self):
        """compute_block with is_diagonal=True must have zero diagonal."""
        from electre3.block import compute_block
        # Small deterministic matrix: N=3 alternatives, C=2 criteria
        G = np.array([
            [1.0, 2.0],
            [3.0, 1.0],
            [2.0, 3.0],
        ], dtype=np.float64)
        q = np.array([0.1, 0.1], dtype=np.float64)
        p = np.array([0.5, 0.5], dtype=np.float64)
        v = np.array([1.0, 1.0], dtype=np.float64)
        weights = np.array([0.5, 0.5], dtype=np.float64)
        # Compute diagonal block (same rows and cols)
        S = compute_block(G, G, q, p, v, weights, is_diagonal=True)
        # Diagonal S(a,a) must be exactly zero
        assert np.allclose(np.diag(S), 0.0), f"Diagonal not zero: {np.diag(S)}"
        # Off-diagonal can be non-zero (verifies test isn't trivial)
        assert not np.allclose(S, 0.0), "All zeros - test may be trivial"

    def test_compute_block_diagonal_false_not_zeroed(self):
        """compute_block with is_diagonal=False should NOT zero diagonal."""
        from electre3.block import compute_block
        G = np.array([
            [1.0, 2.0],
            [3.0, 1.0],
            [2.0, 3.0],
        ], dtype=np.float64)
        q = np.array([0.1, 0.1], dtype=np.float64)
        p = np.array([0.5, 0.5], dtype=np.float64)
        v = np.array([1.0, 1.0], dtype=np.float64)
        weights = np.array([0.5, 0.5], dtype=np.float64)
        # Compute as non-diagonal block
        S = compute_block(G, G, q, p, v, weights, is_diagonal=False)
        # Diagonal should NOT be zeroed (S(a,a) can be non-zero when not cleared)
        # For same G rows/cols, S(a,a) before clearing is typically 1.0
        diag = np.diag(S)
        # At least one diagonal should be non-zero (proves zeroing only happens when flagged)
        assert np.any(diag > 0), f"Diagonal all zero even without is_diagonal=True: {diag}"

    def test_multiblock_ranking_no_self_comparison_leakage(self):
        """Multi-block ranking must not leak self-comparisons across blocks."""
        # When N > block_size, diagonal blocks are processed separately.
        # This test verifies the ranking completes without NaN and produces valid order.
        G = np.array([
            [1.0, 2.0],
            [2.0, 3.0],
            [3.0, 1.0],
            [4.0, 2.0],
            [5.0, 3.0],
        ])
        criteria = [
            CriterionConfig("c1", weight=1.0, q=0.1, p=0.5, v=1.0),
            CriterionConfig("c2", weight=1.0, q=0.1, p=0.5, v=1.0),
        ]
        config = ComputeConfig(block_size=2)  # Force 3 diagonal blocks
        ranking, acc = compute_ranking(G, criteria, config)
        assert len(ranking) == 5
        assert not np.isnan(ranking).any()
        # All indices should appear exactly once (valid permutation)
        assert set(ranking) == {0, 1, 2, 3, 4}
