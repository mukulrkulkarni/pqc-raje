"""Integration tests for ELECTRE III ranking system."""

import numpy as np
import pytest
from electre3.config import CriterionConfig, ComputeConfig
from electre3.ranking import compute_ranking
from electre3.bruteforce import bruteforce_ranking


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_small_problem(self):
        """Complete ranking of a small problem."""
        G = np.array([
            [80.0, 70.0, 90.0],
            [75.0, 85.0, 80.0],
            [90.0, 60.0, 85.0],
            [85.0, 75.0, 70.0],
        ])
        criteria = [
            CriterionConfig("Price", weight=0.4, q=5, p=10, v=20),
            CriterionConfig("Quality", weight=0.35, q=3, p=8, v=15),
            CriterionConfig("Speed", weight=0.25, q=2, p=5, v=12),
        ]
        ranking, acc = compute_ranking(G, criteria)
        assert len(ranking) == 4
        assert set(ranking) == {0, 1, 2, 3}
        assert acc.blocks_done >= 1

    def test_cost_benefit_mix(self):
        """Mix of cost and benefit criteria."""
        G = np.array([
            [100.0, 90.0],  # High cost, high quality
            [50.0, 80.0],   # Low cost, medium quality
            [75.0, 95.0],   # Medium cost, high quality
        ])
        criteria = [
            CriterionConfig("Cost", weight=0.5, q=10, p=20, v=40, maximize=False),
            CriterionConfig("Quality", weight=0.5, q=5, p=10, v=20),
        ]
        ranking, _ = compute_ranking(G, criteria)
        # Alternative 2 should rank well (medium cost, high quality)
        assert 2 in ranking[:2]

    def test_veto_effect(self):
        """Veto should demote otherwise good alternatives."""
        G = np.array([
            [100.0, 100.0, 0.0],   # Great except one veto
            [80.0, 80.0, 80.0],    # Consistently good
            [70.0, 70.0, 70.0],    # Consistently decent
        ])
        criteria = [
            CriterionConfig("A", weight=0.33, q=5, p=10, v=20),
            CriterionConfig("B", weight=0.33, q=5, p=10, v=20),
            CriterionConfig("C", weight=0.34, q=5, p=10, v=20),
        ]
        ranking, _ = compute_ranking(G, criteria)
        # Alternative 0 should be demoted due to veto on C
        assert ranking[0] == 1  # Consistent performer wins

    def test_large_scale(self):
        """Larger scale problem."""
        N, C = 500, 8
        np.random.seed(42)
        G = np.random.rand(N, C) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=5, p=10, v=20)
            for i in range(C)
        ]
        config = ComputeConfig(block_size=100)
        ranking, acc = compute_ranking(G, criteria, config)
        assert len(ranking) == N
        assert acc.blocks_done == 25  # 5 x 5 blocks


class TestDeterminism:
    """Tests for reproducible results."""

    def test_same_result_multiple_runs(self):
        """Multiple runs should give identical results."""
        G = np.random.rand(20, 4) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=3, p=8, v=15)
            for i in range(4)
        ]
        rankings = [compute_ranking(G, criteria)[0] for _ in range(3)]
        assert all(np.array_equal(rankings[0], r) for r in rankings)

    def test_block_size_independence(self):
        """Different block sizes should give same ranking."""
        G = np.random.rand(30, 3) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=5, p=10, v=20)
            for i in range(3)
        ]
        rankings = []
        for bs in [10, 15, 30]:
            config = ComputeConfig(block_size=bs)
            r, _ = compute_ranking(G, criteria, config)
            rankings.append(r)
        assert all(np.array_equal(rankings[0], r) for r in rankings)

    def test_bruteforce_match(self):
        """Blocked and bruteforce should match."""
        G = np.random.rand(25, 5) * 100
        criteria = [
            CriterionConfig(f"C{i}", weight=np.random.rand() + 0.1, q=5, p=10, v=20)
            for i in range(5)
        ]
        blocked_r, _ = compute_ranking(G, criteria)
        brute_r = bruteforce_ranking(G, criteria)
        assert np.array_equal(blocked_r, brute_r)


class TestEdgeCases:
    """Edge case tests."""

    def test_two_alternatives(self):
        """Minimum viable problem size."""
        G = np.array([[80.0, 70.0], [75.0, 85.0]])
        criteria = [
            CriterionConfig("A", weight=0.5, q=5, p=10, v=20),
            CriterionConfig("B", weight=0.5, q=5, p=10, v=20),
        ]
        ranking, _ = compute_ranking(G, criteria)
        assert len(ranking) == 2

    def test_single_criterion(self):
        """Single criterion problem."""
        G = np.array([[80.0], [60.0], [90.0]])
        criteria = [CriterionConfig("Only", weight=1, q=5, p=10, v=20)]
        ranking, _ = compute_ranking(G, criteria)
        assert ranking[0] == 2  # Highest value

    def test_identical_alternatives(self):
        """All identical alternatives."""
        G = np.ones((5, 3)) * 50
        criteria = [
            CriterionConfig(f"C{i}", weight=1, q=5, p=10, v=20)
            for i in range(3)
        ]
        ranking, acc = compute_ranking(G, criteria)
        # Net flow should be zero for all
        assert np.allclose(acc.net_flow(), 0)

    def test_extreme_weights(self):
        """One dominant criterion."""
        G = np.array([
            [100.0, 50.0],
            [50.0, 100.0],
        ])
        criteria = [
            CriterionConfig("Important", weight=100, q=5, p=10, v=20),
            CriterionConfig("Minor", weight=1, q=5, p=10, v=20),
        ]
        ranking, _ = compute_ranking(G, criteria)
        assert ranking[0] == 0  # High on important criterion

    def test_tight_thresholds(self):
        """Very tight thresholds (q=p=v)."""
        G = np.array([[80.0, 70.0], [75.0, 85.0]])
        criteria = [
            CriterionConfig("A", weight=0.5, q=0, p=0, v=0),
            CriterionConfig("B", weight=0.5, q=0, p=0, v=0),
        ]
        ranking, _ = compute_ranking(G, criteria)
        assert len(ranking) == 2

    def test_wide_thresholds(self):
        """Very wide thresholds."""
        G = np.array([[80.0, 70.0], [75.0, 85.0]])
        criteria = [
            CriterionConfig("A", weight=0.5, q=100, p=200, v=500),
            CriterionConfig("B", weight=0.5, q=100, p=200, v=500),
        ]
        ranking, _ = compute_ranking(G, criteria)
        assert len(ranking) == 2
