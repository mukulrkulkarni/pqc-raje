"""validate.py deep tutorial: executable contracts + negatives.

These tests cover the exact ValueError contracts that the deep tutorial documents.
"""

from __future__ import annotations

import numpy as np
import pytest

from electre3.config import CriterionConfig
from electre3.validate import (
    normalize_weights,
    validate_arrays_match,
    validate_matrix,
    validate_thresholds,
)


class DummyCriterion:
    """A minimal stand-in to exercise validate.py independently of CriterionConfig."""

    def __init__(self, name: str, weight: float, q: float, p: float, v: float):
        self.name = name
        self.weight = weight
        self.q = q
        self.p = p
        self.v = v


def test_validate_matrix_rejects_not_2d() -> None:
    with pytest.raises(ValueError, match=r"Matrix must be 2D"):
        validate_matrix(np.ones(3), n_criteria=3)


def test_validate_matrix_rejects_too_few_alternatives() -> None:
    with pytest.raises(ValueError, match=r"Need at least 2 alternatives"):
        validate_matrix(np.ones((1, 3)), n_criteria=3)


def test_validate_matrix_rejects_wrong_columns() -> None:
    with pytest.raises(ValueError, match=r"Matrix has 2 columns, expected 3"):
        validate_matrix(np.ones((2, 2)), n_criteria=3)


def test_validate_matrix_rejects_nan_and_inf() -> None:
    G = np.ones((2, 1))
    G[0, 0] = np.nan
    with pytest.raises(ValueError, match=r"Matrix contains NaN values"):
        validate_matrix(G, n_criteria=1)

    G = np.ones((2, 1))
    G[0, 0] = np.inf
    with pytest.raises(ValueError, match=r"Matrix contains infinite values"):
        validate_matrix(G, n_criteria=1)


def test_validate_thresholds_enforces_ordering() -> None:
    c = DummyCriterion('c', weight=1.0, q=-1.0, p=0.0, v=1.0)
    with pytest.raises(ValueError, match=r"Criterion 'c': q must be >= 0"):
        validate_thresholds([c])

    c = DummyCriterion('c', weight=1.0, q=2.0, p=1.0, v=3.0)
    with pytest.raises(ValueError, match=r"Criterion 'c': p must be >= q"):
        validate_thresholds([c])

    c = DummyCriterion('c', weight=1.0, q=1.0, p=3.0, v=2.0)
    with pytest.raises(ValueError, match=r"Criterion 'c': v must be >= p"):
        validate_thresholds([c])


def test_normalize_weights_rejects_nonfinite_and_nonpositive_total() -> None:
    # validate.py checks NaN/Inf inside normalize_weights.
    c1 = DummyCriterion('c1', weight=np.nan, q=0.0, p=1.0, v=2.0)
    with pytest.raises(ValueError, match=r"Weights contain NaN values"):
        normalize_weights([c1])

    c2 = DummyCriterion('c2', weight=np.inf, q=0.0, p=1.0, v=2.0)
    with pytest.raises(ValueError, match=r"Weights contain infinite values"):
        normalize_weights([c2])

    c3 = DummyCriterion('c3', weight=0.0, q=0.0, p=1.0, v=2.0)
    c4 = DummyCriterion('c4', weight=0.0, q=0.0, p=1.0, v=2.0)
    with pytest.raises(ValueError, match=r"Total weight must be > 0"):
        normalize_weights([c3, c4])


def test_normalize_weights_outputs_sum_one_and_preserves_ratios() -> None:
    cs = [
        CriterionConfig('c1', weight=2.0, q=0.0, p=1.0, v=2.0),
        CriterionConfig('c2', weight=3.0, q=0.0, p=1.0, v=2.0),
    ]
    w = normalize_weights(cs)
    np.testing.assert_allclose(w.sum(), 1.0)
    np.testing.assert_allclose(w, [0.4, 0.6])


def test_validate_arrays_match_accepts_equal_lengths() -> None:
    validate_arrays_match(np.ones(2), np.ones(2), np.ones(2), np.ones(2))


def test_validate_arrays_match_rejects_length_mismatch() -> None:
    with pytest.raises(ValueError, match=r"Array length mismatch"):
        validate_arrays_match(np.ones(1), np.ones(2), np.ones(1), np.ones(1))
