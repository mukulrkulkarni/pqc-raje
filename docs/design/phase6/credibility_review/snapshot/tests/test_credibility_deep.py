"""Credibility tutorial evidence and mathematical contract regression tests."""
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
import numpy as np
import pytest
from app import create_app
from electre3.credibility import credibility

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/modules/credibility_tutorial_side_by_side.html'


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags, self.text = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, text):
        self.text.append(text)


def plain(html):
    return ''.join(Document(html).text)


def ids(html):
    values = [a['id'] for _, a in Document(html).tags if 'id' in a]
    assert len(values) == len(set(values)), 'Duplicate anchor'
    return values


def resolve_link(href, html):
    url = urlsplit(href)
    assert not url.scheme and not url.netloc, 'External link'
    target = (PAGE.parent / url.path).resolve() if url.path else PAGE
    assert target.is_relative_to(PAGE.parent), 'Path escapes docs'
    assert target.is_file(), 'Missing target'
    target_ids = ids(target.read_text(encoding='utf-8')) if url.path else ids(html)
    assert not url.fragment or url.fragment in target_ids, 'Missing fragment'


def test_n1_layout_and_live_controls():
    html = PAGE.read_text(encoding='utf-8')
    anchors = ids(html)
    assert anchors.index('notation') < anchors.index('io') < anchors.index('example')
    doc = Document(html)
    assert [a.get('src') for t,a in doc.tags if t == 'script'] == ['assets/theme.js','assets/highlight.js']
    assert {'light','dark','system'} == {a['data-theme-value'] for _,a in doc.tags if 'data-theme-value' in a}
    for r in range(1,6):
        assert f'jump-R{r}' in anchors
        row = html.split(f'id="row-R{r}"',1)[1].split('</section>',1)[0]
        head = next(a for _,a in Document(row).tags if a.get('role') == 'button')
        assert head['aria-pressed'] == 'false' and head['tabindex'] == '0'
        for heading in ['Purpose','I/O','Why','Pitfalls']:
            content = plain(row.split(f'<h4>{heading}</h4>',1)[1].split('<h4>',1)[0])
            assert len(content.split()) >= 20
    for id_ in ['example','backlinks']:
        assert any(t == 'details' and a.get('id') == id_ and 'open' not in a for t,a in doc.tags)
    assert '[Placeholder]' not in html and 'S &le; C always' not in html


def test_style_notation_and_sample_remain_consistent():
    html = PAGE.read_text(encoding='utf-8')
    concordance = (PAGE.parent/'concordance_tutorial_side_by_side.html').read_text(encoding='utf-8')
    discordance = (PAGE.parent/'discordance_tutorial_side_by_side.html').read_text(encoding='utf-8')
    for pattern in [r'<style>.*?</style>',r'<section class="card" id="notation".*?</section>']:
        ours = re.search(pattern,html,re.S).group().replace('CREDIBILITY MODULE','CONCORDANCE MODULE')
        assert ours == re.search(pattern,concordance,re.S).group()
    pattern = r'<details class="ex" id="example">.*?</details>'
    assert re.search(pattern,html,re.S).group() == re.search(pattern,discordance,re.S).group()


def test_source_excerpts_and_highlights_are_exact():
    html = PAGE.read_text(encoding='utf-8')
    source = (ROOT/'electre3/credibility.py').read_text(encoding='utf-8').splitlines()
    ranges = {1:list(range(1,6)),2:[6,27],3:[30,31,32,34,35],4:list(range(37,44)),5:list(range(40,46))}
    for r,numbers in ranges.items():
        row = html.split(f'id="row-R{r}"',1)[1].split('</section>',1)[0]
        code = row.split('<pre><code>',1)[1].split('</code></pre>',1)[0]
        assert [int(n) for n in re.findall(r'<span class="ln">(\d+)</span>',code)] == numbers
        code = re.sub(r'<span class="ln">\d+</span>','',code)
        assert plain(code) == '\n'.join(source[n-1] for n in numbers)
    assert '<span class="hl">' in html


def test_execute_example_matches_displayed_table(capsys):
    html = PAGE.read_text(encoding='utf-8')
    usage = html.split('id="usage"',1)[1].split('</section>',1)[0]
    code = plain(usage.split('<pre><code>',1)[1].split('</code></pre>',1)[0])
    state = {}
    exec(compile(code,'<credibility-tutorial>','exec'),state)
    table = html.split('id="scenario-results"',1)[1].split('</table>',1)[0]
    rows = re.findall(r'<tr>(.*?)</tr>',table,re.S)[1:]
    assert len(rows) == len(state['results']) == 3
    for row,(second,d,C,S) in zip(rows,state['results']):
        cells = [plain(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',row,re.S)]
        assert float(cells[0]) == second
        np.testing.assert_allclose(d,[[[0.,float(Fraction(cells[2])),0.]]])
        np.testing.assert_allclose(C,[[float(cells[3])]])
        np.testing.assert_allclose(S,[[float(Fraction(cells[4].split('≈')[0].strip()))]])
    reverse = np.array([[[-2.,5.5,-1.]]])
    d = state['discordance'](reverse,state['p'],state['v'])
    c = state['partial_concordance'](reverse,state['q'],state['p'])
    C = state['global_concordance'](c,state['weights'])
    np.testing.assert_allclose(credibility(C,d),[[.75]])
    assert capsys.readouterr().out


@pytest.mark.parametrize('support,opposition,expected', [
    (.6,[.2,.6],.6), (.6,[.8,.9],.075),
    (1.,[0.,np.nextafter(1.,0.)],1.), (1.,[0.,1.],0.),
    (.6,[1.,.8],0.), (.6,[.8,1.],0.), (0.,[0.,.8],0.),
])
def test_formula_contract_boundaries(support,opposition,expected):
    C = np.array([[support]]); d = np.array([[opposition]])
    before = [C.copy(),d.copy()]
    with np.errstate(divide='raise',invalid='raise'):
        S = credibility(C,d)
    np.testing.assert_allclose(S,[[expected]],rtol=1e-12,atol=1e-15)
    assert not np.shares_memory(S,C)
    for actual,original in zip((C,d),before):
        np.testing.assert_array_equal(actual,original)


def test_masks_use_original_concordance_not_running_score():
    # First objection reduces S from .6 to .3. A later .5 must NOT reduce it.
    for values in [[.8,.5],[.5,.8]]:
        np.testing.assert_allclose(credibility(np.array([[.6]]),np.array([[values]])),[[.3]])


def test_rectangular_shape_valid_bounds_and_permutation():
    C = np.array([[.2,.5,.9],[0.,1.,.7]])
    d = np.array([[[.4,.8],[.6,.9],[.2,.95]],[[.1,.8],[.3,.6],[1.,.4]]])
    S = credibility(C,d)
    assert S.shape == (2,3)
    assert ((S >= 0) & (S <= C+1e-15)).all()
    np.testing.assert_allclose(S,credibility(C,d[:,:,::-1]))


def test_lowlevel_invalid_inputs_are_not_silently_called_valid():
    assert credibility(np.array([[.7]]),np.array([[[np.nan]]])).item() == .7
    assert np.isnan(credibility(np.array([[np.nan]]),np.array([[[.2]]])).item())
    # Empty criterion axis is not rejected here; enforce at the boundary.
    assert credibility(np.array([[.7]]),np.empty((1,1,0))).item() == .7
    # Clipping invalid support -0.2 to 0 violates S<=C for invalid input.
    assert credibility(np.array([[-.2]]),np.array([[[0.]]])).item() == 0.
    with pytest.raises((ValueError,IndexError)):
        credibility(np.ones((1,1))*.7,np.ones((2,2,1)))
    with pytest.raises(TypeError):
        credibility(np.array([[0]],dtype=int),np.array([[[.5]]]))
    # No self-comparison clearing in this function.
    np.testing.assert_array_equal(np.diag(credibility(np.ones((2,2)),np.zeros((2,2,1)))),[1.,1.])


def test_all_local_links_and_http_targets():
    html = PAGE.read_text(encoding='utf-8')
    client = create_app({'TESTING':True}).test_client()
    for tag,a in Document(html).tags:
        if tag != 'a' or 'href' not in a:
            continue
        resolve_link(a['href'],html)
        if not urlsplit(a['href']).path:
            continue
        url = urljoin('/docs/modules/credibility/tutorial',a['href'])
        response = client.get(urlsplit(url).path)
        assert response.status_code == 200
        assert "script-src 'self'" in response.headers['Content-Security-Policy']
        frag = urlsplit(url).fragment
        assert not frag or frag in ids(response.get_data(as_text=True))
        for asset in ['theme.js','highlight.js']:
            assert client.get(urljoin(url,'assets/'+asset)).status_code == 200


@pytest.mark.parametrize('href',['#missing','absent.html','https://example.com','//example.com','../../outside.html'])
def test_link_validation_negatives(href):
    with pytest.raises(AssertionError):
        resolve_link(href,'')
