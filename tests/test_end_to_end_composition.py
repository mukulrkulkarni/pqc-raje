"""End-to-end composition: credibility blocks -> accumulator -> ranking.

This is not ELECTRE III distillation. It verifies the pipeline contracts:
- Blockwise accumulation matches an independently computed full reference.
- Diagonal exclusion applies only to diagonal blocks.
- Invalid inputs fail before compute_block is called.
- Sorting uses raw net flow, not normalize().
"""

from __future__ import annotations

import numpy as np
import pytest

from electre3.accumulator import NetFlowAccumulator
from electre3.block import compute_block
from electre3.config import CriterionConfig, ComputeConfig
from electre3.concordance import global_concordance, partial_concordance
from electre3.credibility import credibility
from electre3.discordance import discordance
from electre3.ranking import compute_ranking
import electre3.ranking as ranking_module


def criteria() -> list[CriterionConfig]:
    # Same shape as other deep tests; cost is minimize.
    return [
        CriterionConfig('quality', 0.6, 1.0, 3.0, 6.0),
        CriterionConfig('cost', 0.4, 1.0, 3.0, 6.0, maximize=False),
    ]


def full_reference_net_flow(G: np.ndarray, cs: list[CriterionConfig]) -> np.ndarray:
    adj = G.copy()
    # minimize columns are negated by the pipeline; emulate that here
    for j, c in enumerate(cs):
        if not c.maximize:
            adj[:, j] *= -1

    diff = adj[:, None, :] - adj[None, :, :]
    q = np.array([c.q for c in cs], dtype=float)
    p = np.array([c.p for c in cs], dtype=float)
    v = np.array([c.v for c in cs], dtype=float)
    w = np.array([c.weight for c in cs], dtype=float)
    w = w / w.sum()

    S = credibility(global_concordance(partial_concordance(diff, q, p), w), discordance(diff, p, v))
    np.fill_diagonal(S, 0.0)

    return S.sum(axis=1) - S.sum(axis=0)


@pytest.mark.parametrize('B', [1, 2, 3])
def test_end_to_end_blockwise_matches_full_reference(B: int) -> None:
    G = np.array(
        [
            [10.0, 7.0],
            [8.0, 4.0],
            [5.0, 8.0],
            [11.0, 5.0],
        ]
    )
    cs = criteria()

    flow_ref = full_reference_net_flow(G, cs)
    order, acc = compute_ranking(G, cs, ComputeConfig(block_size=B))

    np.testing.assert_allclose(acc.net_flow(), flow_ref, atol=1e-14)
    assert set(order) == set(range(G.shape[0]))
    assert np.all(np.diff(acc.net_flow()[order]) <= 1e-14)


def test_end_to_end_diagonal_contract() -> None:
    # Distinct objects can be identical; only true diagonal blocks clear diagonal.
    rows = np.array([[1.0, 1.0]])
    cols = np.array([[1.0, 1.0]])
    q = np.ones(2)
    p = np.ones(2) * 3
    v = np.ones(2) * 6
    w = np.array([0.6, 0.4])

    S_off = compute_block(rows, cols, q, p, v, w, is_diagonal=False)
    assert S_off.shape == (1, 1)
    assert S_off.item() == 1.0

    S_diag = compute_block(rows, cols, q, p, v, w, is_diagonal=True)
    assert S_diag.item() == 0.0


def test_end_to_end_invalid_input_fails_before_block(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail('Invalid input reached compute_block')

    monkeypatch.setattr(ranking_module, 'compute_block', forbidden)

    with pytest.raises(ValueError):
        compute_ranking(np.array([[np.nan, 1.0], [2.0, 3.0]]), criteria())


def test_end_to_end_sorting_never_uses_normalize(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail('Ranking should sort raw net flow')

    monkeypatch.setattr(NetFlowAccumulator, 'normalize', forbidden)
    order, acc = compute_ranking(np.array([[10.0, 7.0], [8.0, 4.0], [5.0, 8.0]]), criteria())
    assert np.all(np.diff(acc.net_flow()[order]) <= 0)
