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
