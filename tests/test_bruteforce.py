"""Tests for bruteforce reference implementation."""

import numpy as np
import pytest
from electre3.config import CriterionConfig
from electre3.bruteforce import bruteforce_ranking
from electre3.ranking import compute_ranking


class TestBruteforceRanking:
    """Tests for bruteforce ranking computation."""

    @pytest.fixture
    def simple_matrix(self):
        """Simple test matrix."""
        return np.array([
            [80.0, 70.0],
            [75.0, 85.0],
            [90.0, 60.0],
        ])

    @pytest.fixture
    def simple_criteria(self):
        """Simple criteria list."""
        return [
            CriterionConfig("C1", weight=0.6, q=5, p=10, v=20),
            CriterionConfig("C2", weight=0.4, q=3, p=8, v=15),
        ]

    def test_returns_array(self, simple_matrix, simple_criteria):
        """Should return numpy array."""
        ranking = bruteforce_ranking(simple_matrix, simple_criteria)
        assert isinstance(ranking, np.ndarray)

    def test_correct_length(self, simple_matrix, simple_criteria):
        """Should return correct length."""
        ranking = bruteforce_ranking(simple_matrix, simple_criteria)
        assert len(ranking) == 3

    def test_is_permutation(self, simple_matrix, simple_criteria):
        """Should be permutation of indices."""
        ranking = bruteforce_ranking(simple_matrix, simple_criteria)
        assert set(ranking) == {0, 1, 2}

    def test_matches_blocked_implementation(self, simple_matrix, simple_criteria):
        """Should match blocked implementation."""
        bf_ranking = bruteforce_ranking(simple_matrix, simple_criteria)
        blocked_ranking, _ = compute_ranking(simple_matrix, simple_criteria)
        assert np.array_equal(bf_ranking, blocked_ranking)

    def test_dominant_alternative(self):
        """Dominant alternative should rank first."""
        G = np.array([
            [50.0, 50.0],
            [100.0, 100.0],  # Dominant
            [50.0, 50.0],
        ])
        criteria = [
            CriterionConfig("A", weight=0.5, q=5, p=10, v=20),
            CriterionConfig("B", weight=0.5, q=5, p=10, v=20),
        ]
        ranking = bruteforce_ranking(G, criteria)
        assert ranking[0] == 1

    def test_minimize_criterion(self):
        """Should handle cost criteria."""
        G = np.array([
            [100.0, 50.0],
            [50.0, 100.0],
        ])
        criteria = [
            CriterionConfig("Cost", weight=1.0, q=5, p=10, v=30, maximize=False),
            CriterionConfig("Q", weight=0.001, q=5, p=10, v=30),
        ]
        ranking = bruteforce_ranking(G, criteria)
        assert ranking[0] == 1

    def test_deterministic(self, simple_matrix, simple_criteria):
        """Should be deterministic."""
        r1 = bruteforce_ranking(simple_matrix, simple_criteria)
        r2 = bruteforce_ranking(simple_matrix, simple_criteria)
        assert np.array_equal(r1, r2)

    def test_larger_matrix(self):
        """Should work with larger matrices."""
        G = np.random.rand(50, 5) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=5, p=10, v=20)
            for i in range(5)
        ]
        ranking = bruteforce_ranking(G, criteria)
        assert len(ranking) == 50
        assert set(ranking) == set(range(50))


class TestBruteforceVsBlocked:
    """Cross-validation tests between bruteforce and blocked implementations."""

    def test_small_matrix_match(self):
        """Small matrices should match exactly."""
        for _ in range(5):
            G = np.random.rand(10, 3) * 100
            criteria = [
                CriterionConfig(f"C{i}", weight=np.random.rand() + 0.1, q=3, p=8, v=15)
                for i in range(3)
            ]
            bf = bruteforce_ranking(G, criteria)
            blocked, _ = compute_ranking(G, criteria)
            assert np.array_equal(bf, blocked)

    def test_various_block_sizes(self):
        """Should match regardless of block size."""
        G = np.random.rand(20, 2) * 100
        criteria = [
            CriterionConfig("A", weight=0.6, q=5, p=10, v=20),
            CriterionConfig("B", weight=0.4, q=3, p=8, v=15),
        ]
        bf = bruteforce_ranking(G, criteria)

        from electre3.config import ComputeConfig
        for bs in [5, 7, 10, 20]:
            blocked, _ = compute_ranking(G, criteria, ComputeConfig(block_size=bs))
            assert np.array_equal(bf, blocked), f"Mismatch with block_size={bs}"

    def test_with_cost_criteria(self):
        """Should match with minimize criteria."""
        G = np.random.rand(15, 4) * 100
        criteria = [
            CriterionConfig("Benefit1", weight=0.3, q=5, p=10, v=20),
            CriterionConfig("Cost1", weight=0.3, q=5, p=10, v=20, maximize=False),
            CriterionConfig("Benefit2", weight=0.2, q=5, p=10, v=20),
            CriterionConfig("Cost2", weight=0.2, q=5, p=10, v=20, maximize=False),
        ]
        bf = bruteforce_ranking(G, criteria)
        blocked, _ = compute_ranking(G, criteria)
        assert np.array_equal(bf, blocked)
