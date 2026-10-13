"""Tests for electre3.ranking module."""

import numpy as np
import pytest
from electre3.config import CriterionConfig, ComputeConfig
from electre3.ranking import compute_ranking


class TestComputeRanking:
    """Tests for the main ranking function."""

    @pytest.fixture
    def simple_matrix(self):
        """Simple 3x2 matrix for testing."""
        return np.array([
            [80.0, 70.0],
            [75.0, 85.0],
            [90.0, 60.0],
        ])

    @pytest.fixture
    def simple_criteria(self):
        """Simple criteria for testing."""
        return [
            CriterionConfig("C1", weight=0.6, q=5, p=10, v=20),
            CriterionConfig("C2", weight=0.4, q=3, p=8, v=15),
        ]

    def test_returns_tuple(self, simple_matrix, simple_criteria):
        """Should return (ranking, accumulator) tuple."""
        result = compute_ranking(simple_matrix, simple_criteria)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_ranking_shape(self, simple_matrix, simple_criteria):
        """Ranking should have same length as alternatives."""
        ranking, _ = compute_ranking(simple_matrix, simple_criteria)
        assert ranking.shape == (3,)

    def test_ranking_is_permutation(self, simple_matrix, simple_criteria):
        """Ranking should be a permutation of [0, 1, ..., N-1]."""
        ranking, _ = compute_ranking(simple_matrix, simple_criteria)
        assert set(ranking) == {0, 1, 2}

    def test_accumulator_has_data(self, simple_matrix, simple_criteria):
        """Accumulator should have processed blocks."""
        _, acc = compute_ranking(simple_matrix, simple_criteria)
        assert acc.blocks_done > 0
        assert acc.n_alternatives == 3

    def test_deterministic(self, simple_matrix, simple_criteria):
        """Same inputs should give same ranking."""
        ranking1, _ = compute_ranking(simple_matrix, simple_criteria)
        ranking2, _ = compute_ranking(simple_matrix, simple_criteria)
        assert np.array_equal(ranking1, ranking2)

    def test_dominant_alternative_ranks_first(self):
        """Alternative dominating all others should rank first."""
        G = np.array([
            [50.0, 50.0],
            [100.0, 100.0],  # Dominates
            [50.0, 50.0],
        ])
        criteria = [
            CriterionConfig("C1", weight=0.5, q=5, p=10, v=20),
            CriterionConfig("C2", weight=0.5, q=5, p=10, v=20),
        ]
        ranking, _ = compute_ranking(G, criteria)
        assert ranking[0] == 1  # Dominant alternative

    def test_custom_block_size(self, simple_matrix, simple_criteria):
        """Should work with custom block size."""
        config = ComputeConfig(block_size=2)
        ranking, acc = compute_ranking(simple_matrix, simple_criteria, config)
        assert acc.blocks_done >= 1
        assert len(ranking) == 3

    def test_minimize_criterion(self):
        """Should handle cost criteria (minimize)."""
        G = np.array([
            [100.0, 50.0],  # High cost
            [50.0, 100.0],  # Low cost
        ])
        criteria = [
            CriterionConfig("Cost", weight=1.0, q=5, p=10, v=30, maximize=False),
            CriterionConfig("Quality", weight=0.0001, q=5, p=10, v=30),
        ]
        ranking, _ = compute_ranking(G, criteria)
        # Lower cost should rank better
        assert ranking[0] == 1

    def test_single_criterion(self):
        """Should work with single criterion."""
        G = np.array([[80.0], [60.0], [90.0]])
        criteria = [CriterionConfig("Only", weight=1, q=5, p=10, v=20)]
        ranking, _ = compute_ranking(G, criteria)
        assert ranking[0] == 2  # Highest value

    def test_many_alternatives(self):
        """Should handle many alternatives."""
        N = 100
        C = 4
        G = np.random.rand(N, C) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=5, p=10, v=20)
            for i in range(C)
        ]
        ranking, acc = compute_ranking(G, criteria)
        assert len(ranking) == N
        assert acc.n_alternatives == N

    def test_net_flow_ordering(self, simple_matrix, simple_criteria):
        """Ranking should be ordered by descending net flow."""
        ranking, acc = compute_ranking(simple_matrix, simple_criteria)
        net_flow = acc.net_flow()

        # Check ordering
        for i in range(len(ranking) - 1):
            assert net_flow[ranking[i]] >= net_flow[ranking[i + 1]]

    def test_invalid_matrix_raises(self, simple_criteria):
        """Invalid matrix should raise ValueError."""
        G = np.array([[1.0, np.nan], [2.0, 3.0]])
        with pytest.raises(ValueError):
            compute_ranking(G, simple_criteria)

    def test_empty_criteria_raises(self, simple_matrix):
        """Empty criteria list should raise."""
        with pytest.raises((ValueError, IndexError)):
            compute_ranking(simple_matrix, [])

    def test_default_config(self, simple_matrix, simple_criteria):
        """Should work without explicit config."""
        ranking, _ = compute_ranking(simple_matrix, simple_criteria)
        assert len(ranking) == 3
