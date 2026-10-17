"""Discordance deep tutorial: executable evidence, content contracts and negatives."""
from fractions import Fraction
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

import numpy as np
import pytest
from app import create_app
from electre3.concordance import partial_concordance
from electre3.discordance import discordance
from electre3.credibility import credibility

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/modules/discordance_tutorial_side_by_side.html'


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags, self.text = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def plain(html):
    return ''.join(Document(html).text)


def ids(html):
    values = [a['id'] for _, a in Document(html).tags if 'id' in a]
    assert len(values) == len(set(values)), 'Duplicate IDs'
    return values


def check_links(html):
    local_ids = ids(html)
    for tag, attrs in Document(html).tags:
        if tag != 'a' or 'href' not in attrs:
            continue
        url = urlsplit(attrs['href'])
        assert not url.scheme and not url.netloc, 'Nonlocal URL'
        target = (PAGE.parent / url.path).resolve() if url.path else PAGE
        assert target.is_relative_to(PAGE.parent), 'Escaping path'
        assert target.is_file(), 'Missing file'
        anchors = ids(target.read_text(encoding='utf-8')) if url.path else local_ids
        assert not url.fragment or url.fragment in anchors, 'Missing fragment'


def test_n1_structure_and_live_control_contract():
    html = PAGE.read_text(encoding='utf-8')
    anchors = ids(html)
    assert anchors.index('notation') < anchors.index('io') < anchors.index('example')
    assert '[Placeholder]' not in html and '~0.1 ms' not in html
    tags = Document(html).tags
    assert [a.get('src') for t, a in tags if t == 'script'] == ['assets/theme.js', 'assets/highlight.js']
    for r in range(1, 6):
        row = html.split(f'id="row-R{r}"', 1)[1].split('</section>', 1)[0]
        assert f'id="jump-R{r}"' in html
        for label in ['Purpose', 'I/O', 'Why', 'Pitfalls']:
            text = plain(row.split(f'<h4>{label}</h4>', 1)[1].split('<h4>', 1)[0])
            assert len(text.split()) >= 20, (r, label)
        head = next(a for _, a in Document(row).tags if a.get('role') == 'button')
        assert head['aria-pressed'] == 'false' and head['tabindex'] == '0'
    for id_ in ['example', 'backlinks']:
        assert any(t == 'details' and a.get('id') == id_ and 'open' not in a for t, a in tags)
    assert {'light', 'dark', 'system'} == {a['data-theme-value'] for _, a in tags if 'data-theme-value' in a}


def test_style_and_notation_identical_to_approved_concordance():
    html = PAGE.read_text(encoding='utf-8')
    reference = (PAGE.parent / 'concordance_tutorial_side_by_side.html').read_text(encoding='utf-8')
    for pattern in [r'<style>.*?</style>', r'<section class="card" id="notation".*?</section>']:
        actual = re.search(pattern, html, re.S).group().replace('DISCORDANCE MODULE', 'CONCORDANCE MODULE')
        assert actual == re.search(pattern, reference, re.S).group()


def test_code_excerpts_match_actual_source():
    html = PAGE.read_text(encoding='utf-8')
    source = (ROOT / 'electre3/discordance.py').read_text(encoding='utf-8').splitlines()
    for r, lo, hi in [(1, 1, 4), (2, 6, 8), (3, 27, 30), (4, 32, 34), (5, 28, 34)]:
        row = html.split(f'id="row-R{r}"', 1)[1].split('</section>', 1)[0]
        code = row.split('<pre><code>', 1)[1].split('</code></pre>', 1)[0]
        without_numbers = re.sub(r'<span class="ln">\d+</span>', '', code)
        assert plain(without_numbers) == '\n'.join(source[lo-1:hi])


def test_execute_usage_and_compare_visible_table(capsys):
    html = PAGE.read_text(encoding='utf-8')
    usage = html.split('id="usage"', 1)[1].split('</section>', 1)[0]
    code = plain(usage.split('<pre><code>', 1)[1].split('</code></pre>', 1)[0])
    namespace = {}
    exec(compile(code, '<discordance-tutorial>', 'exec'), namespace)
    table = html.split('id="scenario-results"', 1)[1].split('</table>', 1)[0]
    rows = re.findall(r'<tr>(.*?)</tr>', table, re.S)[1:]
    assert len(rows) == len(namespace['results']) == 3
    for row, (second, d, C, S) in zip(rows, namespace['results']):
        cells = [plain(x) for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)]
        assert float(cells[0]) == second
        expected_d = float(Fraction(cells[2]))
        expected_S = float(Fraction(cells[4].split('≈')[0].strip()))
        np.testing.assert_allclose(d, [[[0., expected_d, 0.]]])
        np.testing.assert_allclose(C, [[float(cells[3])]])
        np.testing.assert_allclose(S, [[expected_S]])
    assert capsys.readouterr().out
    np.testing.assert_array_equal(namespace['B'], [8., 7., 6.])
    # Independently check the reverse direction used in the prose.
    reverse = np.array([[[-2., 5.5, -1.]]])
    d = discordance(reverse, namespace['p'], namespace['v'])
    c = partial_concordance(reverse, namespace['q'], namespace['p'])
    C = namespace['global_concordance'](c, namespace['weights'])
    np.testing.assert_allclose(C, [[.75]])
    np.testing.assert_allclose(credibility(C, d), [[.75]])


@pytest.mark.parametrize('diff,expected', [(-6.,1.),(-5.5,5/6),(-3.,0.),(0.,0.)])
def test_strict_threshold_endpoints_and_interpolation(diff, expected):
    value = discordance(np.array([[[diff]]]), np.array([3.]), np.array([6.]))
    assert value.item() == pytest.approx(expected)


@pytest.mark.parametrize('diff,expected', [(-3.001,1.),(-3.,1.),(-2.999,0.)])
def test_equal_threshold_veto_first(diff, expected):
    with np.errstate(divide='raise', invalid='raise'):
        value = discordance(np.array([[[diff]]]), np.array([3.]), np.array([3.]))
    assert value.item() == expected


def test_opposition_is_not_complement_of_concordance():
    diff = np.array([[[-3.]]])
    c = partial_concordance(diff, np.array([1.]), np.array([3.]))
    d = discordance(diff, np.array([3.]), np.array([6.]))
    assert c.item() == d.item() == 0.
    assert d.item() != (1-c).item()


def test_rectangular_blocks_monotonic_and_inputs_unchanged():
    diff = np.array([[[-7.,0.],[-4.,1.],[-3.,2.]], [[0.,-8.],[2.,-5.],[4.,-2.]]])
    p, v = np.array([3.,2.]), np.array([6.,5.])
    originals = [a.copy() for a in (diff,p,v)]
    result = discordance(diff,p,v)
    assert result.shape == (2,3,2)
    assert ((result >= 0) & (result <= 1)).all()
    assert (discordance(diff+.1,p,v) <= result+1e-14).all()
    for actual, expected in zip((diff,p,v), originals):
        np.testing.assert_array_equal(actual, expected)


def test_no_reduction_below_global_concordance_and_veto_at_one():
    C = np.array([[.7,.7,1.]])
    d = np.array([[[.5],[.7],[1.]]])
    np.testing.assert_allclose(credibility(C,d), [[.7,.7,0.]])


def test_lowlevel_nonfinite_and_mismatch_are_not_validation():
    result = discordance(np.array([[[np.nan,np.inf,-np.inf]]]), np.ones(3), np.full(3,2.))
    assert np.isnan(result[0,0,0])
    np.testing.assert_array_equal(result[0,0,1:], [0.,1.])
    with pytest.raises(ValueError):
        discordance(np.zeros((1,1,3)), np.ones(2), np.ones(2)*2)
    # Length one silently broadcasts: documentation must not promise rejection.
    assert discordance(np.zeros((1,1,3)), np.ones(1), np.ones(1)*2).shape == (1,1,3)


def test_local_links_and_served_assets():
    html = PAGE.read_text(encoding='utf-8')
    check_links(html)
    client = create_app({'TESTING':True}).test_client()
    for tag,a in Document(html).tags:
        if tag != 'a' or not urlsplit(a.get('href','')).path:
            continue
        url = urljoin('/docs/modules/discordance/tutorial',a['href'])
        response = client.get(urlsplit(url).path)
        assert response.status_code == 200
        assert "script-src 'self'" in response.headers['Content-Security-Policy']
        fragment = urlsplit(url).fragment
        assert not fragment or fragment in ids(response.get_data(as_text=True))
        for asset in ('theme.js','highlight.js'):
            assert client.get(urljoin(url,'assets/'+asset)).status_code == 200


@pytest.mark.parametrize('link',['#absent','missing.html','https://example.com','//example.com','../../outside.html'])
def test_invalid_links_rejected(link):
    with pytest.raises(AssertionError):
        check_links(f'<a href="{link}">bad</a>')
