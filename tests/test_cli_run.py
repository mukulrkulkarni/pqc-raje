"""Tests for CLI run functionality under the strict shared contract."""

import numpy as np
import pytest

from electre3.cli_run import format_preview, run_ranking


def _criteria():
    return [
        {"name": "A", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True},
        {"name": "B", "weight": 0.5, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True},
    ]


class TestFormatPreview:
    def test_shows_shape_and_statistics(self):
        matrix = np.array([[0.1, 0.2], [0.3, 0.4]])
        preview = format_preview(matrix, _criteria())
        assert "2 alt" in preview
        assert "Min" in preview and "Max" in preview and "Mean" in preview

    def test_warns_about_nonfinite_preview_values(self):
        preview = format_preview(np.array([[0.1, np.nan], [0.3, np.inf]]), _criteria())
        assert "NaN" in preview
        assert "Infinite" in preview


class TestRunRanking:
    def test_returns_ranking_permutation(self):
        ranking = run_ranking(np.array([[0.8, 0.2], [0.2, 0.8]]), _criteria(), quiet=True)
        assert isinstance(ranking, np.ndarray)
        assert set(ranking) == {0, 1}

    def test_accepts_block_size_in_shared_range(self):
        ranking = run_ranking(np.array([[0.8, 0.2], [0.2, 0.8]]), _criteria(), block_size=1, quiet=True)
        assert len(ranking) == 2

    def test_cost_criterion_uses_normalized_scores(self):
        criteria = [
            {"name": "cost", "weight": 1.0, "q": 0.0, "p": 0.1, "v": 0.5, "maximize": False},
        ]
        ranking = run_ranking(np.array([[1.0], [0.0]]), criteria, quiet=True)
        assert ranking[0] == 1

    @pytest.mark.parametrize("criteria", [
        [{"weight": 1.0, "q": 0.0, "p": 0.2, "v": 0.5, "maximize": True}],
        [{"name": "A", "weight": 1.0, "q": 0.0, "p": 0.2, "v": 0.5}],
    ])
    def test_rejects_incomplete_legacy_criteria(self, criteria):
        with pytest.raises(ValueError):
            run_ranking(np.array([[0.1], [0.2]]), criteria, quiet=True)

    def test_rejects_unnormalized_scores(self):
        with pytest.raises(ValueError, match="normalized"):
            run_ranking(np.array([[2.0, 0.2], [0.3, 0.4]]), _criteria(), quiet=True)

    def test_is_deterministic(self):
        matrix = np.array([[0.8, 0.2], [0.4, 0.6], [0.1, 0.9]])
        np.testing.assert_array_equal(
            run_ranking(matrix, _criteria(), quiet=True),
            run_ranking(matrix, _criteria(), quiet=True),
        )
