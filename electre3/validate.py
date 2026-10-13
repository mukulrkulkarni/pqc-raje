"""Validation functions for ELECTRE III inputs."""

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import CriterionConfig


def validate_thresholds(criteria: list["CriterionConfig"]) -> None:
    """Validate that all criteria have valid threshold ordering.

    Args:
        criteria: List of criterion configurations.

    Raises:
        ValueError: If any threshold ordering is violated.
    """
    for c in criteria:
        if c.q < 0:
            raise ValueError(f"Criterion '{c.name}': q must be >= 0, got {c.q}")
        if c.p < c.q:
            raise ValueError(f"Criterion '{c.name}': p must be >= q")
        if c.v < c.p:
            raise ValueError(f"Criterion '{c.name}': v must be >= p")


def normalize_weights(criteria: list["CriterionConfig"]) -> np.ndarray:
    """Normalize criterion weights to sum to 1.0.

    Args:
        criteria: List of criterion configurations.

    Returns:
        Array of normalized weights.

    Raises:
        ValueError: If total weight is zero or negative.
    """
    weights = np.array([c.weight for c in criteria], dtype=np.float64)
    total = weights.sum()
    if total <= 0:
        raise ValueError(f"Total weight must be > 0, got {total}")
    return weights / total


def validate_matrix(G: np.ndarray, n_criteria: int) -> None:
    """Validate performance matrix dimensions and values.

    Args:
        G: Performance matrix of shape (N, C).
        n_criteria: Expected number of criteria.

    Raises:
        ValueError: If matrix is invalid.
    """
    if G.ndim != 2:
        raise ValueError(f"Matrix must be 2D, got {G.ndim}D")
    if G.shape[0] < 2:
        raise ValueError(f"Need at least 2 alternatives, got {G.shape[0]}")
    if G.shape[1] != n_criteria:
        raise ValueError(f"Matrix has {G.shape[1]} columns, expected {n_criteria}")
    if np.isnan(G).any():
        raise ValueError("Matrix contains NaN values")
    if np.isinf(G).any():
        raise ValueError("Matrix contains infinite values")
