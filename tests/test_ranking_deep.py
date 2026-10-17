"""Ranking tutorial: executable example, independent block checks and negatives."""
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urljoin, urlsplit
import numpy as np
import pytest
from app import create_app
from electre3.config import CriterionConfig, ComputeConfig
from electre3.ranking import compute_ranking
from electre3.block import compute_block
from electre3.concordance import partial_concordance, global_concordance
from electre3.discordance import discordance
from electre3.credibility import credibility
from electre3.accumulator import NetFlowAccumulator
import electre3.ranking as ranking_module

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT/'docs/modules/ranking_tutorial_side_by_side.html'


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags, self.text = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))

    def handle_data(self, text):
        self.text.append(text)


def plain(html):
    return ''.join(Document(html).text)


def anchors(html):
    values = [a['id'] for _,a in Document(html).tags if 'id' in a]
    assert len(values) == len(set(values))
    return values


def check_link(href, html):
    url = urlsplit(href)
    assert not url.scheme and not url.netloc
    target = (PAGE.parent/url.path).resolve() if url.path else PAGE
    assert target.is_relative_to(PAGE.parent) and target.is_file()
    ids = anchors(target.read_text(encoding='utf-8')) if url.path else anchors(html)
    assert not url.fragment or url.fragment in ids


def criteria():
    return [CriterionConfig('quality',.6,1.,3.,6.), CriterionConfig('cost',.4,1.,3.,6.,maximize=False)]


def test_structure_style_and_live_controls():
    html = PAGE.read_text(encoding='utf-8')
    reference = (PAGE.parent/'concordance_tutorial_side_by_side.html').read_text(encoding='utf-8')
    ids = anchors(html)
    assert ids.index('notation') < ids.index('io') < ids.index('example')
    for pattern in [r'<style>.*?</style>',r'<section class="card" id="notation".*?</section>']:
        assert re.search(pattern,html,re.S).group().replace('RANKING MODULE','CONCORDANCE MODULE') == re.search(pattern,reference,re.S).group()
    tags = Document(html).tags
    assert [a.get('src') for t,a in tags if t == 'script'] == ['assets/theme.js','assets/highlight.js']
    assert {'light','dark','system'} == {a['data-theme-value'] for _,a in tags if 'data-theme-value' in a}
    for r in range(1,6):
        row = html.split(f'id="row-R{r}"',1)[1].split('</section>',1)[0]
        assert f'jump-R{r}' in ids
        head = next(a for _,a in Document(row).tags if a.get('role') == 'button')
        assert head['aria-pressed'] == 'false' and head['tabindex'] == '0'
        for label in ['Purpose','I/O','Why','Pitfalls']:
            assert len(plain(row.split(f'<h4>{label}</h4>',1)[1].split('<h4>',1)[0]).split()) >= 20
    for id_ in ['example','backlinks']:
        assert any(t == 'details' and a.get('id') == id_ and 'open' not in a for t,a in tags)


def test_all_source_lines_exact():
    html = PAGE.read_text(encoding='utf-8')
    lines = (ROOT/'electre3/ranking.py').read_text(encoding='utf-8').splitlines()
    for r,lo,hi in [(1,1,11),(2,12,22),(3,23,26),(4,27,32),(5,33,33)]:
        row = html.split(f'id="row-R{r}"',1)[1].split('</section>',1)[0]
        code = row.split('<pre><code>',1)[1].split('</code></pre>',1)[0]
        assert plain(re.sub(r'<span class="ln">\d+</span>','',code)) == '\n'.join(lines[lo-1:hi])


def test_example_computed_table_and_pair_values(capsys):
    html = PAGE.read_text(encoding='utf-8')
    usage = html.split('id="usage"',1)[1].split('</section>',1)[0]
    code = plain(usage.split('<pre><code>',1)[1].split('</code></pre>',1)[0])
    state = {}; exec(compile(code,'<ranking-tutorial>','exec'),state)
    acc = state['acc']
    rows = re.findall(r'<tr>(.*?)</tr>',html.split('id="flow-results"',1)[1].split('</table>',1)[0],re.S)[1:]
    assert len(rows) == 2
    for i,row in enumerate(rows):
        cells = [plain(x) for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',row,re.S)]
        assert cells[0] == state['ids'][i]
        np.testing.assert_allclose([acc.outflow[i],acc.inflow[i],acc.net_flow()[i],acc.normalize()[i]],list(map(float,cells[1:])))
    rows = re.findall(r'<tr>(.*?)</tr>',html.split('id="pair-results"',1)[1].split('</table>',1)[0],re.S)[1:]
    assert len(rows) == 4
    for (i,j),row in zip([(0,0),(0,1),(1,0),(1,1)],rows):
        cells = [plain(x) for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',row,re.S)]
        G = state['G']; q=np.ones(3);p=np.full(3,3.);v=np.full(3,6.)
        S=compute_block(G[i:i+1],G[j:j+1],q,p,v,np.array(state['weights']),is_diagonal=i==j)
        assert S.item() == pytest.approx(float(cells[2]))
    np.testing.assert_array_equal(state['ranked_ids'],['A','B'])
    assert acc.blocks_done == 4 and capsys.readouterr().out


@pytest.mark.parametrize('B',[1,2,3,10])
def test_blocking_matches_independent_full_reference(B):
    G=np.array([[10.,7.],[8.,4.],[5.,8.],[11.,5.],[7.,6.]])
    original=G.copy(); cs=criteria();adj=G.copy();adj[:,1]*=-1
    diff=adj[:,None,:]-adj[None,:,:]
    q=np.ones(2);p=np.full(2,3.);v=np.full(2,6.);w=np.array([.6,.4])
    S=credibility(global_concordance(partial_concordance(diff,q,p),w),discordance(diff,p,v))
    np.fill_diagonal(S,0.)
    order,acc=compute_ranking(G,cs,ComputeConfig(block_size=B))
    np.testing.assert_allclose(acc.outflow,S.sum(axis=1))
    np.testing.assert_allclose(acc.inflow,S.sum(axis=0))
    flow=S.sum(axis=1)-S.sum(axis=0)
    np.testing.assert_allclose(acc.net_flow(),flow,atol=1e-14)
    assert set(order)==set(range(5)) and np.all(np.diff(flow[order]) <= 1e-14)
    assert acc.blocks_done == ((5+B-1)//B)**2
    np.testing.assert_array_equal(G,original)


def test_diagonal_flags_and_local_offdiagonal_positions(monkeypatch):
    G=np.array([[10.,7.],[8.,4.],[5.,8.]])
    calls=[]; real=ranking_module.compute_block
    def spy(rows,cols,q,p,v,w,is_diagonal):
        S=real(rows,cols,q,p,v,w,is_diagonal)
        calls.append((rows.copy(),cols.copy(),is_diagonal,S.copy()))
        return S
    monkeypatch.setattr(ranking_module,'compute_block',spy)
    compute_ranking(G,criteria(),ComputeConfig(block_size=2))
    assert [c[2] for c in calls] == [True,False,False,True]
    assert [c[3].shape for c in calls] == [(2,2),(2,1),(1,2),(1,1)]
    for _,_,flag,S in calls:
        if flag: np.testing.assert_array_equal(np.diag(S),0.)
    # Distinct objects can have identical data; local diagonal must survive.
    S=real(np.array([[1.,1.]]),np.array([[1.,1.]]),np.ones(2),np.ones(2)*3,np.ones(2)*6,np.array([.6,.4]),False)
    assert S.item() == 1.


def test_sorting_never_calls_optional_normalize(monkeypatch):
    def forbidden(*args): pytest.fail('Ranking should sort raw net flow')
    monkeypatch.setattr(NetFlowAccumulator,'normalize',forbidden)
    order,acc=compute_ranking(np.array([[10.,7.],[8.,4.],[5.,8.]]),criteria())
    assert np.all(np.diff(acc.net_flow()[order]) <= 0)


def test_minmax_distinct_from_dividing_by_n_minus_one():
    acc=NetFlowAccumulator(3)
    acc.outflow[:]=[2.,1.,0.];acc.inflow[:]=[0.,1.,2.]
    np.testing.assert_array_equal(acc.normalize(),[1.,.5,0.])
    np.testing.assert_array_equal(acc.net_flow()/2,[1.,0.,-1.])
    acc.outflow[:]=0;acc.inflow[:]=0
    np.testing.assert_array_equal(acc.normalize(),[.5,.5,.5])


def test_equal_scores_do_not_assume_tie_permutation():
    order,acc=compute_ranking(np.ones((3,2)),criteria(),ComputeConfig(block_size=2))
    assert set(order)=={0,1,2}
    np.testing.assert_array_equal(acc.net_flow(),[0.,0.,0.])


@pytest.mark.parametrize('G,cs',[(np.ones((2,2)),[]),(np.ones((1,2)),criteria()),(np.ones(3),criteria()),(np.ones((2,3)),criteria()),(np.array([[np.nan,1.],[2.,3.]]),criteria()),(np.array([[np.inf,1.],[2.,3.]]),criteria())])
def test_invalid_inputs_fail_before_block(monkeypatch,G,cs):
    def forbidden(*args): pytest.fail('Invalid input reached compute_block')
    monkeypatch.setattr(ranking_module,'compute_block',forbidden)
    with pytest.raises(ValueError): compute_ranking(G,cs)


@pytest.mark.parametrize('weight',[np.nan,np.inf,-np.inf])
def test_mutated_nonfinite_weights_rejected(monkeypatch,weight):
    cs=criteria();cs[0].weight=weight
    def forbidden(*args): pytest.fail('Bad weights reached compute_block')
    monkeypatch.setattr(ranking_module,'compute_block',forbidden)
    with pytest.raises(ValueError):compute_ranking(np.ones((2,2)),cs)


def test_invalid_block_size_constructor():
    with pytest.raises(ValueError):ComputeConfig(block_size=0)


def test_documented_ignored_fields_have_no_effect_for_fixed_input():
    G=np.array([[10.,7.],[8.,4.],[5.,8.]])
    order1,a=compute_ranking(G,criteria(),ComputeConfig(block_size=2,seed=1,use_numba=True))
    order2,b=compute_ranking(G,criteria(),ComputeConfig(block_size=2,seed=999,use_numba=False))
    np.testing.assert_array_equal(order1,order2)
    np.testing.assert_array_equal(a.net_flow(),b.net_flow())


def test_local_links_and_http_fragments():
    html=PAGE.read_text(encoding='utf-8');client=create_app({'TESTING':True}).test_client()
    for tag,a in Document(html).tags:
        if tag!='a' or 'href' not in a:continue
        check_link(a['href'],html)
        if not urlsplit(a['href']).path:continue
        url=urljoin('/docs/modules/ranking/tutorial',a['href']);response=client.get(urlsplit(url).path)
        assert response.status_code==200
        assert "script-src 'self'" in response.headers['Content-Security-Policy']
        fragment=urlsplit(url).fragment
        assert not fragment or fragment in anchors(response.get_data(as_text=True))
        for asset in ['theme.js','highlight.js']:
            assert client.get(urljoin(url,'assets/'+asset)).status_code==200


@pytest.mark.parametrize('href',['#missing','missing.html','https://example.com','//example.com','../../escape.html'])
def test_link_negatives(href):
    with pytest.raises(AssertionError):check_link(href,'')


def _jsdom_available() -> bool:
    if shutil.which('node') is None:
        return False
    try:
        res = subprocess.run(['node','-e','require(\'jsdom\');'], capture_output=True, text=True)
    except OSError:
        return False
    return res.returncode == 0


@pytest.mark.skipif(not _jsdom_available(), reason='node+jsdom not available')
def test_keyboard_enter_and_space_toggle(tmp_path: Path) -> None:
    """Regression test for WCAG keyboard toggles on .row-head.

    This is a deterministic jsdom unit test. It does not attempt full browser layout.
    """
    html = PAGE.read_text(encoding='utf-8')
    highlight_js = (PAGE.parent/'assets'/'highlight.js').read_text(encoding='utf-8')

    runner = tmp_path/'runner.js'
    runner.write_text(
        """
const { JSDOM } = require('jsdom');

function fail(msg) {
  console.error(msg);
  process.exit(2);
}

const html = process.env.RANKING_HTML;
const highlight = process.env.HIGHLIGHT_JS;

const dom = new JSDOM(html, { url: 'http://example.local/', runScripts: 'dangerously' });

dom.window.eval(highlight);

const rowHead = dom.window.document.querySelector('.row-head[data-range="R2"]');
if (!rowHead) fail('row-head R2 not found');
const row = dom.window.document.getElementById('row-R2');
if (!row) fail('row-R2 not found');

rowHead.focus();
rowHead.dispatchEvent(new dom.window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
if (!row.classList.contains('sel')) fail('Enter did not select row');
if (rowHead.getAttribute('aria-pressed') !== 'true') fail('aria-pressed not true after Enter');

rowHead.dispatchEvent(new dom.window.KeyboardEvent('keydown', { key: ' ', bubbles: true }));
if (row.classList.contains('sel')) fail('Space did not clear selection');
if (rowHead.getAttribute('aria-pressed') !== 'false') fail('aria-pressed not false after Space toggle-off');

rowHead.dispatchEvent(new dom.window.KeyboardEvent('keydown', { key: ' ', bubbles: true }));
if (!row.classList.contains('sel')) fail('Space did not re-select row');

process.exit(0);
""",
        encoding='utf-8',
    )

    res = subprocess.run(
        ['node', str(runner)],
        cwd=str(tmp_path),
        env={**dict(**__import__('os').environ), 'RANKING_HTML': html, 'HIGHLIGHT_JS': highlight_js},
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stdout + res.stderr


@pytest.mark.skipif(not _jsdom_available(), reason='node+jsdom not available')
def test_missing_row_or_progress_targets_do_not_throw(tmp_path: Path) -> None:
    """Guard clauses must prevent exceptions on missing DOM targets."""
    highlight_js = (PAGE.parent/'assets'/'highlight.js').read_text(encoding='utf-8')

    runner = tmp_path/'runner_missing.js'
    runner.write_text(
        """
const { JSDOM } = require('jsdom');

const highlight = process.env.HIGHLIGHT_JS;
const dom = new JSDOM('<!doctype html><html><body><div class="jump"><a data-range="R9" id="jump-R9">R9</a></div></body></html>', { url: 'http://example.local/', runScripts: 'dangerously' });

dom.window.eval(highlight);

// Should not throw even if row-R9 and prog-txt are missing.
const jump = dom.window.document.getElementById('jump-R9');
jump.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));

process.exit(0);
""",
        encoding='utf-8',
    )

    res = subprocess.run(
        ['node', str(runner)],
        cwd=str(tmp_path),
        env={**dict(**__import__('os').environ), 'HIGHLIGHT_JS': highlight_js},
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stdout + res.stderr
