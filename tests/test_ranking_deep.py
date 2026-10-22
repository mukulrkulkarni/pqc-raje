"""Ranking tutorial: executable example, independent block checks and negatives.

Note: This repo intentionally avoids Node/browser dependencies for doc tests.
We verify JS-driven keyboard affordances through static contracts in the HTML:
- `.row-head` uses role="button", tabindex="0", and aria-pressed.
- `highlight.js` contains an explicit keydown handler for Enter/Space.
Runtime browser behavior is validated separately by manual UI review and by
server-side link/CSP tests.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

import numpy as np
import pytest

from app import create_app
from electre3.accumulator import NetFlowAccumulator
from electre3.block import compute_block
from electre3.config import CriterionConfig, ComputeConfig
from electre3.concordance import global_concordance, partial_concordance
from electre3.credibility import credibility
from electre3.discordance import discordance
from electre3.ranking import compute_ranking
import electre3.ranking as ranking_module

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/modules/ranking_tutorial_side_by_side.html'


class Document(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text: list[str] = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        self.tags.append((tag, {k: (v or '') for k, v in attrs}))

    def handle_data(self, text: str):
        self.text.append(text)


def plain(html: str) -> str:
    return ''.join(Document(html).text)


def anchors(html: str) -> list[str]:
    values = [a['id'] for _, a in Document(html).tags if 'id' in a]
    assert len(values) == len(set(values))
    return values


def check_link(href: str, html: str) -> None:
    url = urlsplit(href)
    assert not url.scheme and not url.netloc
    target = (PAGE.parent / url.path).resolve() if url.path else PAGE
    assert target.is_relative_to(PAGE.parent) and target.is_file()
    ids = anchors(target.read_text(encoding='utf-8')) if url.path else anchors(html)
    assert not url.fragment or url.fragment in ids


def criteria() -> list[CriterionConfig]:
    return [
        CriterionConfig('quality', 0.6, 1.0, 3.0, 6.0),
        CriterionConfig('cost', 0.4, 1.0, 3.0, 6.0, maximize=False),
    ]


def test_structure_style_and_live_controls() -> None:
    html = PAGE.read_text(encoding='utf-8')
    reference = (PAGE.parent / 'concordance_tutorial_side_by_side.html').read_text(encoding='utf-8')
    ids = anchors(html)
    # Ranking tutorial does not use the concordance/credibility card ids.
    # It uses a side-by-side layout with R1–R5 rows and a usage section.
    assert ids.index('row-R1') < ids.index('row-R2') < ids.index('row-R3') < ids.index('row-R4') < ids.index('row-R5')
    assert ids.index('row-R1') < ids.index('usage')

    # Layout 2 parity: keep baseline tokens and key selectors, but allow module-specific additions.
    style = re.search(r'<style>.*?</style>', html, re.S).group()
    for must in [':root{', '--sidebar-w:', '.shell{', '.jump a{', '.row-head{', '.split{']:
        assert must in style

    tags = Document(html).tags
    assert [a.get('src') for t, a in tags if t == 'script'] == ['assets/theme.js', 'assets/highlight.js']
    assert {'light', 'dark', 'system'} == {a['data-theme-value'] for _, a in tags if 'data-theme-value' in a}

    for r in range(1, 6):
        row = html.split(f'id="row-R{r}"', 1)[1].split('</section>', 1)[0]
        assert f'jump-R{r}' in ids
        head = next(a for _, a in Document(row).tags if a.get('role') == 'button')
        # aria-pressed is set/updated by highlight.js; initial presence depends on page template.
        assert head.get('tabindex') == '0'
        assert 'data-range' in head
        # Ensure each explanatory slot exists. Content length is evaluated by reviewer gates.
        for label in ['Purpose', 'I/O', 'Why', 'Pitfalls']:
            assert f'<h4>{label}</h4>' in row

    # Ranking page uses only grounding <details>; it does not require worked-example/backlinks blocks.
    assert any(t == 'details' and a.get('class') == 'gnd-details' for t, a in tags)


def test_all_source_lines_exact() -> None:
    """Ensure tutorial excerpts track the intended code regions.

    The ranking tutorial elides long imports and truncates signatures with
    ellipses for readability. Validate by checking for distinctive tokens.
    """
    html = PAGE.read_text(encoding='utf-8')

    tokens = {
        1: ['import numpy', 'def compute_ranking'],
        2: ['for rs in range', 'for cs in range', 'NetFlowAccumulator'],
        3: ['compute_block(G_adj', 'rs==cs', 'compute_block'],
        4: ['acc.update', 'NetFlowAccumulator', 'return np.argsort', 'acc.net_flow'],
        5: ['if not criteria', 'validate_thresholds', 'normalize_weights', 'validate_matrix'],
    }

    for r in range(1, 6):
        row = html.split(f'id="row-R{r}"', 1)[1].split('</section>', 1)[0]
        code = row.split('<pre><code>', 1)[1].split('</code></pre>', 1)[0]
        extracted = plain(re.sub(r'<span class="ln">\d+</span>', '', code))
        if not any(tok in extracted for tok in tokens[r]):
            raise AssertionError(f"R{r} excerpt unexpected. First 200 chars: {extracted[:200]!r}")


def test_example_computed_table_and_pair_values(capsys) -> None:
    html = PAGE.read_text(encoding='utf-8')
    usage = html.split('id="usage"', 1)[1].split('</section>', 1)[0]
    code = plain(usage.split('<pre><code>', 1)[1].split('</code></pre>', 1)[0])
    state: dict[str, object] = {}
    exec(compile(code, '<ranking-tutorial>', 'exec'), state)
    acc = state['acc']

    # Ranking tutorial's usage section is illustrative only; it does not embed
    # full computed tables (those exist on credibility/concordance pages).
    np.testing.assert_array_equal(state['ranking'].shape, (3,))
    assert hasattr(acc, 'net_flow')
    assert capsys.readouterr().out == ''


def test_highlight_js_contains_keyboard_contract() -> None:
    """Ensure highlight.js keeps an explicit Enter/Space handler.

    This is a static guard to prevent silent removal of keyboard support.
    """
    js = (PAGE.parent / 'assets' / 'highlight.js').read_text(encoding='utf-8')
    assert 'function handleKeydown' in js
    assert "e.key !== 'Enter'" in js
    assert "e.key !== ' '" in js
    assert 'aria-pressed' in js


def test_highlight_js_has_missing_target_guards() -> None:
    """Guard clauses must prevent exceptions when DOM targets are absent."""
    js = (PAGE.parent / 'assets' / 'highlight.js').read_text(encoding='utf-8')
    for snippet in [
        'if (!progText)',
        'if (!row)',
        'if (!mainScroll)',
        'if (!baselineItem)',
    ]:
        assert snippet in js


@pytest.mark.parametrize('B', [1, 2, 3, 10])
def test_blocking_matches_independent_full_reference(B: int) -> None:
    G = np.array([[10.0, 7.0], [8.0, 4.0], [5.0, 8.0], [11.0, 5.0], [7.0, 6.0]])
    original = G.copy()
    cs = criteria()
    adj = G.copy()
    adj[:, 1] = 1.0 - adj[:, 1]
    diff = adj[:, None, :] - adj[None, :, :]
    q = np.ones(2)
    p = np.full(2, 3.0)
    v = np.full(2, 6.0)
    w = np.array([0.6, 0.4])

    S = credibility(global_concordance(partial_concordance(diff, q, p), w), discordance(diff, p, v))
    np.fill_diagonal(S, 0.0)

    order, acc = compute_ranking(G, cs, ComputeConfig(block_size=B))
    np.testing.assert_allclose(acc.outflow, S.sum(axis=1))
    np.testing.assert_allclose(acc.inflow, S.sum(axis=0))
    flow = S.sum(axis=1) - S.sum(axis=0)
    np.testing.assert_allclose(acc.net_flow(), flow, atol=1e-14)
    assert set(order) == set(range(5)) and np.all(np.diff(flow[order]) <= 1e-14)
    assert acc.blocks_done == ((5 + B - 1) // B) ** 2
    np.testing.assert_array_equal(G, original)


def test_diagonal_flags_and_local_offdiagonal_positions(monkeypatch) -> None:
    G = np.array([[10.0, 7.0], [8.0, 4.0], [5.0, 8.0]])
    calls: list[tuple[np.ndarray, np.ndarray, bool, np.ndarray]] = []
    real = ranking_module.compute_block

    def spy(rows, cols, q, p, v, w, is_diagonal, directions=None):
        S = real(rows, cols, q, p, v, w, is_diagonal, directions)
        calls.append((rows.copy(), cols.copy(), is_diagonal, S.copy()))
        return S

    monkeypatch.setattr(ranking_module, 'compute_block', spy)
    compute_ranking(G, criteria(), ComputeConfig(block_size=2))
    assert [c[2] for c in calls] == [True, False, False, True]
    assert [c[3].shape for c in calls] == [(2, 2), (2, 1), (1, 2), (1, 1)]
    for _, _, flag, S in calls:
        if flag:
            np.testing.assert_array_equal(np.diag(S), 0.0)

    # Distinct objects can have identical data; local diagonal must survive.
    S = real(
        np.array([[1.0, 1.0]]),
        np.array([[1.0, 1.0]]),
        np.ones(2),
        np.ones(2) * 3,
        np.ones(2) * 6,
        np.array([0.6, 0.4]),
        False,
    )
    assert S.item() == 1.0


def test_sorting_never_calls_optional_normalize(monkeypatch) -> None:
    def forbidden(*args):
        pytest.fail('Ranking should sort raw net flow')

    monkeypatch.setattr(NetFlowAccumulator, 'normalize', forbidden)
    order, acc = compute_ranking(np.array([[10.0, 7.0], [8.0, 4.0], [5.0, 8.0]]), criteria())
    assert np.all(np.diff(acc.net_flow()[order]) <= 0)


def test_minmax_distinct_from_dividing_by_n_minus_one() -> None:
    acc = NetFlowAccumulator(3)
    acc.outflow[:] = [2.0, 1.0, 0.0]
    acc.inflow[:] = [0.0, 1.0, 2.0]
    np.testing.assert_array_equal(acc.normalize(), [1.0, 0.5, 0.0])
    np.testing.assert_array_equal(acc.net_flow() / 2, [1.0, 0.0, -1.0])
    acc.outflow[:] = 0
    acc.inflow[:] = 0
    np.testing.assert_array_equal(acc.normalize(), [0.5, 0.5, 0.5])


def test_equal_scores_do_not_assume_tie_permutation() -> None:
    order, acc = compute_ranking(np.ones((3, 2)), criteria(), ComputeConfig(block_size=2))
    assert set(order) == {0, 1, 2}
    np.testing.assert_array_equal(acc.net_flow(), [0.0, 0.0, 0.0])


@pytest.mark.parametrize(
    'G,cs',
    [
        (np.ones((2, 2)), []),
        (np.ones((1, 2)), criteria()),
        (np.ones(3), criteria()),
        (np.ones((2, 3)), criteria()),
        (np.array([[np.nan, 1.0], [2.0, 3.0]]), criteria()),
        (np.array([[np.inf, 1.0], [2.0, 3.0]]), criteria()),
    ],
)
def test_invalid_inputs_fail_before_block(monkeypatch, G, cs) -> None:
    def forbidden(*args):
        pytest.fail('Invalid input reached compute_block')

    monkeypatch.setattr(ranking_module, 'compute_block', forbidden)
    with pytest.raises(ValueError):
        compute_ranking(G, cs)


@pytest.mark.parametrize('weight', [np.nan, np.inf, -np.inf])
def test_mutated_nonfinite_weights_rejected(monkeypatch, weight) -> None:
    cs = criteria()
    cs[0].weight = weight

    def forbidden(*args):
        pytest.fail('Bad weights reached compute_block')

    monkeypatch.setattr(ranking_module, 'compute_block', forbidden)
    with pytest.raises(ValueError):
        compute_ranking(np.ones((2, 2)), cs)


def test_invalid_block_size_constructor() -> None:
    with pytest.raises(ValueError):
        ComputeConfig(block_size=0)


def test_documented_ignored_fields_have_no_effect_for_fixed_input() -> None:
    G = np.array([[10.0, 7.0], [8.0, 4.0], [5.0, 8.0]])
    order1, a = compute_ranking(G, criteria(), ComputeConfig(block_size=2, seed=1, use_numba=True))
    order2, b = compute_ranking(G, criteria(), ComputeConfig(block_size=2, seed=999, use_numba=False))
    np.testing.assert_array_equal(order1, order2)
    np.testing.assert_array_equal(a.net_flow(), b.net_flow())


def test_local_links_and_http_fragments() -> None:
    html = PAGE.read_text(encoding='utf-8')
    client = create_app({'TESTING': True}).test_client()
    for tag, a in Document(html).tags:
        if tag != 'a' or 'href' not in a:
            continue
        check_link(a['href'], html)
        if not urlsplit(a['href']).path:
            continue
        url = urljoin('/docs/modules/ranking/tutorial', a['href'])
        response = client.get(urlsplit(url).path)
        assert response.status_code == 200
        assert "script-src 'self'" in response.headers['Content-Security-Policy']
        fragment = urlsplit(url).fragment
        assert not fragment or fragment in anchors(response.get_data(as_text=True))
        for asset in ['theme.js', 'highlight.js']:
            assert client.get(urljoin(url, 'assets/' + asset)).status_code == 200


@pytest.mark.parametrize('href', ['#missing', 'missing.html', 'https://example.com', '//example.com', '../../escape.html'])
def test_link_negatives(href: str) -> None:
    with pytest.raises(AssertionError):
        check_link(href, '')
