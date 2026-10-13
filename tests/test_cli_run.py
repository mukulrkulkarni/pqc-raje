"""Tests for CLI run functionality."""

import json
import numpy as np
import pytest
import tempfile
from pathlib import Path
from io import StringIO
import sys

from electre3.cli_run import format_preview, run_ranking


class TestFormatPreview:
    """Tests for CLI preview formatting."""

    def test_shows_shape(self):
        """Preview should show matrix shape."""
        matrix = np.random.rand(100, 5)
        criteria = [{"name": f"C{i}", "weight": 1, "q": 1, "p": 2, "v": 3} for i in range(5)]
        preview = format_preview(matrix, criteria)
        assert "100" in preview
        assert "5" in preview

    def test_shows_dtype(self):
        """Preview should show data type."""
        matrix = np.random.rand(10, 2)
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3}]
        preview = format_preview(matrix, criteria)
        assert "float" in preview.lower()

    def test_shows_statistics(self):
        """Preview should show min/max/mean."""
        matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3}]
        preview = format_preview(matrix, criteria)
        assert "Min" in preview
        assert "Max" in preview
        assert "Mean" in preview

    def test_shows_criteria_count(self):
        """Preview should show number of criteria."""
        matrix = np.random.rand(10, 3)
        criteria = [{"name": f"C{i}", "weight": 1, "q": 1, "p": 2, "v": 3} for i in range(3)]
        preview = format_preview(matrix, criteria)
        assert "3" in preview

    def test_shows_nan_warning(self):
        """Preview should warn about NaN values."""
        matrix = np.array([[1.0, np.nan], [3.0, 4.0]])
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3}]
        preview = format_preview(matrix, criteria)
        assert "NaN" in preview

    def test_shows_inf_warning(self):
        """Preview should warn about infinite values."""
        matrix = np.array([[1.0, np.inf], [3.0, 4.0]])
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3}]
        preview = format_preview(matrix, criteria)
        assert "infinite" in preview

    def test_shows_pair_count(self):
        """Preview should show pairwise comparison count."""
        matrix = np.random.rand(100, 3)
        criteria = [{"name": "A", "weight": 1, "q": 1, "p": 2, "v": 3}]
        preview = format_preview(matrix, criteria)
        assert "10,000" in preview  # 100 * 100

    def test_shows_criterion_details(self):
        """Preview should show each criterion's parameters."""
        matrix = np.random.rand(10, 2)
        criteria = [
            {"name": "Price", "weight": 2, "q": 5, "p": 10, "v": 20},
            {"name": "Quality", "weight": 1, "q": 3, "p": 8, "v": 15},
        ]
        preview = format_preview(matrix, criteria)
        assert "Price" in preview
        assert "Quality" in preview


class TestRunRanking:
    """Tests for CLI ranking execution."""

    def test_returns_array(self):
        """Should return numpy array."""
        matrix = np.random.rand(10, 2)
        criteria = [
            {"name": "A", "weight": 1, "q": 1, "p": 2, "v": 5},
            {"name": "B", "weight": 1, "q": 1, "p": 2, "v": 5},
        ]
        ranking = run_ranking(matrix, criteria, quiet=True)
        assert isinstance(ranking, np.ndarray)

    def test_ranking_length(self):
        """Ranking should have same length as alternatives."""
        matrix = np.random.rand(25, 3)
        criteria = [{"name": f"C{i}", "weight": 1, "q": 1, "p": 2, "v": 5} for i in range(3)]
        ranking = run_ranking(matrix, criteria, quiet=True)
        assert len(ranking) == 25

    def test_ranking_is_permutation(self):
        """Ranking should be permutation of indices."""
        matrix = np.random.rand(10, 2)
        criteria = [
            {"name": "A", "weight": 1, "q": 1, "p": 2, "v": 5},
            {"name": "B", "weight": 1, "q": 1, "p": 2, "v": 5},
        ]
        ranking = run_ranking(matrix, criteria, quiet=True)
        assert set(ranking) == set(range(10))

    def test_custom_block_size(self):
        """Should accept custom block size."""
        matrix = np.random.rand(20, 2)
        criteria = [
            {"name": "A", "weight": 1, "q": 1, "p": 2, "v": 5},
            {"name": "B", "weight": 1, "q": 1, "p": 2, "v": 5},
        ]
        ranking = run_ranking(matrix, criteria, block_size=5, quiet=True)
        assert len(ranking) == 20

    def test_handles_default_name(self):
        """Should handle criteria without name field."""
        matrix = np.random.rand(5, 2)
        criteria = [
            {"weight": 1, "q": 1, "p": 2, "v": 5},
            {"weight": 1, "q": 1, "p": 2, "v": 5},
        ]
        ranking = run_ranking(matrix, criteria, quiet=True)
        assert len(ranking) == 5

    def test_handles_maximize_false(self):
        """Should handle cost criteria."""
        matrix = np.array([[100.0, 50.0], [50.0, 100.0]])
        criteria = [
            {"name": "Cost", "weight": 1, "q": 5, "p": 10, "v": 30, "maximize": False},
            {"name": "Quality", "weight": 0.001, "q": 5, "p": 10, "v": 30},
        ]
        ranking = run_ranking(matrix, criteria, quiet=True)
        assert ranking[0] == 1  # Lower cost is better

    def test_deterministic(self):
        """Same inputs should give same ranking."""
        matrix = np.random.rand(15, 3)
        criteria = [{"name": f"C{i}", "weight": 1, "q": 1, "p": 2, "v": 5} for i in range(3)]

        ranking1 = run_ranking(matrix, criteria, quiet=True)
        ranking2 = run_ranking(matrix, criteria, quiet=True)
        assert np.array_equal(ranking1, ranking2)
