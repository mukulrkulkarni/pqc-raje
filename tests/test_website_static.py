"""Static companion website smoke tests.

These tests enforce basic hardening invariants for the website/ folder:
- no external asset references (http/https) except cross-subdomain navigation links
- tutorial pages reference local assets via ../assets/
- landing priority exists as pages and links are relative

Note: this validates *repo artifacts*, not a deployed host.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).parent.parent
WEBSITE = ROOT / "website"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_website_index_exists() -> None:
    assert (WEBSITE / "index.html").exists()


def test_modules_index_exists() -> None:
    assert (WEBSITE / "modules" / "index.html").exists()


def test_no_external_assets_in_website_html() -> None:
    """Reject CDN/script/style/img external refs.

    Allow exceptions:
    - navigation links to app/docs subdomains (anchors only)
    """
    html_files = list(WEBSITE.rglob("*.html"))
    assert html_files, "Expected website HTML files"

    external = re.compile(r"(src|href)=\"https?://", re.IGNORECASE)

    for path in html_files:
        text = _read(path)
        for m in external.finditer(text):
            snippet = text[m.start() : m.start() + 120]
            # Allow anchor navigation to app/docs domains or local Flask.
            if (
                'href="https://app.' in snippet
                or 'href="https://docs.' in snippet
                or 'href="http://localhost:5000' in snippet
            ):
                continue
            raise AssertionError(f"External asset reference in {path}: {snippet}")


def test_tutorial_pages_reference_local_assets() -> None:
    """Tutorials copied under /modules/<name>/tutorial/ must use ../assets/"""
    for tut in WEBSITE.rglob("modules/*/tutorial/index.html"):
        text = _read(tut)
        assert 'src="../assets/theme.js"' in text
        assert 'src="../assets/highlight.js"' in text


def test_tutorial_pages_have_primary_nav_back_links() -> None:
    for tut in WEBSITE.rglob("modules/*/tutorial/index.html"):
        text = _read(tut)
        assert 'aria-label="Primary"' in text
        assert 'href="/index.html"' in text
        assert 'href="/modules/index.html"' in text
        # User requested both website and Flask back-links.
        assert 'href="http://localhost:5000/"' in text
        assert 'href="http://localhost:5000/docs/modules"' in text


def test_getting_started_has_color_scheme_meta() -> None:
    for path in [WEBSITE / "index.html"]:
        text = _read(path)
        assert 'name="color-scheme"' in text
