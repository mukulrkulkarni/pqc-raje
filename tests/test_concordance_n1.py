"""N1 pilot contracts: DOM order, executable examples, links and negative cases.
Static checks do not substitute for browser keyboard/alignment verification.
"""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit

import numpy as np
import pytest
from app import create_app
from electre3.concordance import partial_concordance, global_concordance

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'docs/modules/concordance_tutorial_side_by_side.html'


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags, self.text = [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def checked_ids(text):
    ids = [a['id'] for _, a in Document(text).tags if 'id' in a]
    assert len(ids) == len(set(ids)), 'Duplicate id'
    return ids


def assert_local_links(text):
    ids = checked_ids(text)
    for tag, attrs in Document(text).tags:
        if tag != 'a' or 'href' not in attrs:
            continue
        link = urlsplit(attrs['href'])
        assert not link.scheme and not link.netloc, 'Nonlocal link'
        target = (PAGE.parent / link.path).resolve() if link.path else PAGE
        assert target.is_relative_to(ROOT / 'docs/modules'), 'Escaping link'
        assert target.is_file(), 'Missing local page'
        target_ids = checked_ids(target.read_text(encoding='utf-8')) if link.path else ids
        assert not link.fragment or link.fragment in target_ids, 'Missing concept anchor'


def test_notation_before_io_and_real_controls():
    html = PAGE.read_text(encoding='utf-8')
    ids = checked_ids(html)
    assert ids.index('notation') < ids.index('io') < ids.index('example')
    doc = Document(html)
    scripts = [a['src'] for t, a in doc.tags if t == 'script']
    assert scripts == ['assets/theme.js', 'assets/highlight.js']
    for r in range(1, 6):
        assert f'row-R{r}' in ids and f'jump-R{r}' in ids
    heads = [a for _, a in doc.tags if a.get('role') == 'button']
    assert len(heads) == 5
    assert all(a.get('tabindex') == '0' and a.get('aria-pressed') == 'false' for a in heads)
    assert all('aria-expanded' not in a for a in heads)
    assert {'light', 'dark', 'system'} == {a['data-theme-value'] for _, a in doc.tags if 'data-theme-value' in a}
    assert all('data-range' not in a for _, a in doc.tags if a.get('href') == '#usage')


def test_fallback_math_and_collapsible_content_without_renderer():
    html = PAGE.read_text(encoding='utf-8')
    doc = Document(html)
    for id_ in ['example', 'backlinks']:
        attrs = next(a for t, a in doc.tags if t == 'details' and a.get('id') == id_)
        assert 'open' not in attrs
    text = ''.join(doc.text)
    assert 'a and b are objects' in text
    assert 'not groups of data fields' in text and '[[[d1, d2, d3]]]' in text
    assert '0.85' in text and '0.75' in text
    assert '<sub>' in html and 'class="math"' in html
    assert 'cdn.' not in html and 'display:none' not in html.split('id="example"', 1)[1]
    assert 'stdout' not in html and '~0.1 ms' not in html
    assert 'collapse to the same test' not in html


def test_runnable_example_matches_displayed_values(capsys):
    html = PAGE.read_text(encoding='utf-8')
    usage = html.split('id="usage"', 1)[1].split('</section>', 1)[0]
    code = usage.split('<pre><code>', 1)[1].split('</code></pre>', 1)[0]
    code = ''.join(Document(code).text)
    values = {}
    exec(compile(code, '<tutorial-example>', 'exec'), values)
    np.testing.assert_allclose(values['C_ab'], [[.85]])
    np.testing.assert_allclose(values['c_j'], [[[1., .5, 1.]]])
    reverse = partial_concordance(-values['diff'], values['q'], values['p'])
    np.testing.assert_allclose(global_concordance(reverse, values['weights']), [[.75]])
    assert '.85' in capsys.readouterr().out


@pytest.mark.parametrize('difference,expected', [(-1.01, 0.), (-1., 1.), (-.99, 1.)])
def test_equal_threshold_boundary_matches_tutorial(difference, expected):
    result = partial_concordance(np.array([[[difference]]]), np.array([1.]), np.array([1.]))
    assert result.item() == expected


def test_all_concept_links_exist_offline_and_served():
    html = PAGE.read_text(encoding='utf-8')
    assert_local_links(html)
    client = create_app({'TESTING': True}).test_client()
    for tag, a in Document(html).tags:
        if tag != 'a' or not urlsplit(a.get('href', '')).path:
            continue
        url = urljoin('/docs/modules/concordance/tutorial', a['href'])
        response = client.get(urlsplit(url).path)
        assert response.status_code == 200, url
        assert "script-src 'self'" in response.headers['Content-Security-Policy']
        frag = urlsplit(url).fragment
        assert not frag or frag in checked_ids(response.get_data(as_text=True))
        for asset in ['theme.js', 'highlight.js']:
            assert client.get(urljoin(url, 'assets/' + asset)).status_code == 200


@pytest.mark.parametrize('link', ['https://example.com', '//example.com/a',
    '#missing', 'missing_tutorial_side_by_side.html', '../../outside.html'])
def test_link_checker_rejects_bad_references(link):
    with pytest.raises(AssertionError):
        assert_local_links(f'<a href="{link}">broken</a>')


@pytest.mark.parametrize('path', [
    '/docs/modules/concordance/notallowed_tutorial_side_by_side.html',
    '/docs/modules/notallowed/config_tutorial_side_by_side.html',
    '/docs/modules/concordance/..%2Fconfig_tutorial_side_by_side.html',
    '/docs/modules/concordance/%2e%2e%2f%2e%2e%2fsecret_tutorial_side_by_side.html',
    '/docs/modules/concordance/data_tutorial_side_by_side.html',
])
def test_sibling_route_rejects_unknown_missing_and_traversal(path):
    assert create_app({'TESTING': True}).test_client().get(path).status_code == 404


def luminance(color):
    rgb = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055)**2.4 for c in rgb]
    return sum(a*b for a, b in zip(linear, [.2126, .7152, .0722]))


def test_selected_badge_contrast_and_system_theme():
    html = PAGE.read_text(encoding='utf-8')
    for selector in [':root', 'html[data-theme="dark"]']:
        rules = re.findall(re.escape(selector) + r'\{([^}]+)\}', html)
        tokens = dict(re.findall(r'(--[\w-]+):\s*(#[\da-fA-F]{6})', '\n'.join(rules)))
        a, b = sorted([luminance(tokens['--sel-fg']), luminance(tokens['--sel-accent'])])
        assert (b+.05)/(a+.05) >= 4.5
    assert '.row.sel .rk,.row:target .rk{color:var(--sel-fg);}' in html
    assert 'html[data-theme="system"]' in html and '@media(prefers-color-scheme:dark)' in html
    # The former white-on-light-green badge must fail this same metric.
    a, b = sorted([luminance('#ffffff'), luminance('#86efac')])
    assert (b+.05)/(a+.05) < 4.5
