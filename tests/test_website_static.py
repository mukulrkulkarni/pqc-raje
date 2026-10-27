"""Static companion website smoke tests.

These tests enforce basic hardening invariants for the website/ folder:
- no external asset references (http/https) except cross-subdomain navigation links
- tutorial pages reference local assets via ../../assets/
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
    """Tutorials copied under /modules/<name>/tutorial/ use ../../assets/."""
    for tut in WEBSITE.rglob("modules/*/tutorial/index.html"):
        text = _read(tut)
        assert 'src="../../assets/theme.js"' in text
        assert 'src="../../assets/highlight.js"' in text


def test_tutorial_pages_have_primary_nav_back_links() -> None:
    tuts = list(WEBSITE.rglob("modules/*/tutorial/index.html"))
    assert tuts, "Expected at least one tutorial page"
    for tut in tuts:
        text = _read(tut)
        assert 'aria-label="Primary"' in text
        assert 'href="/index.html"' in text
        assert 'href="/modules/index.html"' in text
        # User requested both website and Flask back-links.
        assert 'href="http://localhost:5000/"' in text
        assert 'href="http://localhost:5000/docs/modules"' in text


def test_build_website_rebuilds_without_error() -> None:
    """Build should fail fast on malformed tutorial HTML."""
    import subprocess
    r = subprocess.run(["python", "scripts/build_website.py"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_inject_primary_nav_rejects_malformed_body() -> None:
    from scripts.build_website import inject_primary_nav
    import pytest

    bad = "<html><bodyguard>nope</bodyguard></html>"
    with pytest.raises(ValueError):
        inject_primary_nav(bad, active_href="/modules/x/tutorial/")


def test_inject_primary_nav_injects_after_real_body_not_bodyguard() -> None:
    from scripts.build_website import inject_primary_nav

    html = "<html><bodyguard>ignore</bodyguard><body><div>x</div></body></html>"
    out = inject_primary_nav(html, active_href="/modules/x/tutorial/")
    assert out.find("<body>") < out.find('aria-label="Primary"')
    assert out.find("<bodyguard>") < out.find("<body>")


def test_inject_primary_nav_rejects_existing_nav_missing_required_links() -> None:
    from scripts.build_website import inject_primary_nav
    import pytest

    html = "<html><body><nav aria-label=\"Primary\"><a href=\"/index.html\">Home</a></nav></body></html>"
    with pytest.raises(ValueError):
        inject_primary_nav(html, active_href="/modules/x/tutorial/")


def test_getting_started_has_color_scheme_meta() -> None:
    for path in [WEBSITE / "index.html"]:
        text = _read(path)
        assert 'name="color-scheme"' in text
