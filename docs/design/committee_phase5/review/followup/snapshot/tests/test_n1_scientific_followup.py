"""Focused regression coverage for the N1 scientific gate follow-up."""
import numpy as np
import pytest
import electre3.ranking as ranking_module
from electre3.config import CriterionConfig
from electre3.credibility import credibility


@pytest.mark.parametrize('bad_weight,message', [
    (np.nan, 'Weights contain NaN'),
    (np.inf, 'Weights contain infinite'),
    (-np.inf, 'Weights contain infinite'),
])
def test_ranking_rejects_nonfinite_mutated_weights_before_compute(monkeypatch, bad_weight, message):
    # Constructor already rejects these. Mutate the public, mutable dataclass
    # to test the ranking entry point itself, not merely __post_init__.
    criterion = CriterionConfig('quality', weight=1., q=0., p=1., v=2.)
    criterion.weight = bad_weight
    calls = []

    def unexpected_compute(*args, **kwargs):
        calls.append(True)
        pytest.fail('Invalid weights reached block computation')

    monkeypatch.setattr(ranking_module, 'compute_block', unexpected_compute)
    with pytest.raises(ValueError, match=message):
        ranking_module.compute_ranking(np.array([[1.], [2.]]), [criterion])
    assert calls == []


def test_ranking_accepts_finite_weight_and_computes_blocks():
    criterion = CriterionConfig('quality', weight=1., q=0., p=1., v=2.)
    order, accumulator = ranking_module.compute_ranking(np.array([[1.], [2.]]), [criterion])
    assert set(order) == {0, 1}
    assert accumulator.blocks_done > 0
    assert np.isfinite(accumulator.net_flow()).all()


@pytest.mark.parametrize('discordances,expected', [
    ([0., np.nextafter(1., 0.)], 1.),
    ([0., 1.], 0.),
    ([1., 0.], 0.),
])
def test_full_veto_at_perfect_concordance(discordances, expected):
    C = np.array([[1.]])
    d = np.array([[discordances]])
    result = credibility(C, d)
    np.testing.assert_allclose(result, [[expected]], rtol=0, atol=0)
    np.testing.assert_array_equal(C, [[1.]])
    np.testing.assert_array_equal(d, [[discordances]])
