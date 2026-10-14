"""Tests for generated module documentation HTML files (static file validation)."""

import re
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).parent.parent / "docs" / "modules"

# Patterns that indicate external resources (security negative test - should NOT be present)
EXTERNAL_PATTERNS = [
    r'href="https?://',
    r'src="https?://',
    r'url\(["\']?https?://',
    r'@import\s+["\']https?://',
]

# CSP meta tag pattern
CSP_PATTERN = r'<meta\s+http-equiv="Content-Security-Policy"'


class TestTutorialStaticFile:
    """Tests for config_tutorial_side_by_side.html static file validation."""

    @pytest.fixture
    def tutorial_html(self) -> str:
        """Load config_tutorial_side_by_side.html content."""
        path = DOCS_DIR / "config_tutorial_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_no_external_assets(self, tutorial_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, tutorial_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_csp_meta_tag(self, tutorial_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, tutorial_html), "Missing CSP meta tag"

    def test_csp_meta_no_unsafe_eval(self, tutorial_html):
        """CSP meta tag must not contain 'unsafe-eval'."""
        csp_match = re.search(r'content="([^"]*)"', tutorial_html)
        if csp_match:
            csp = csp_match.group(1)
            assert "'unsafe-eval'" not in csp, "CSP should not allow unsafe-eval"

    def test_has_threshold_docs(self, tutorial_html):
        """Tutorial must document threshold semantics."""
        content_lower = tutorial_html.lower()
        assert "indifference" in content_lower, "Missing indifference threshold docs"
        assert "preference" in content_lower, "Missing preference threshold docs"
        assert "veto" in content_lower, "Missing veto threshold docs"

    def test_has_layout2_structure(self, tutorial_html):
        """Tutorial must have Layout 2 structure elements."""
        assert 'class="shell"' in tutorial_html, "Missing .shell grid"
        assert 'class="sidebar"' in tutorial_html, "Missing .sidebar"
        assert 'class="rows"' in tutorial_html, "Missing .rows container"


class TestHTMLValidity:
    """Basic HTML validity tests for all docs/modules/*.html files."""

    @pytest.fixture
    def all_html_files(self) -> list[Path]:
        """Get all HTML files in docs/modules."""
        if not DOCS_DIR.exists():
            pytest.skip("docs/modules directory does not exist")
        return list(DOCS_DIR.glob("*.html"))

    def test_html_files_exist(self, all_html_files):
        """At least one HTML file should exist."""
        assert len(all_html_files) >= 1

    def test_all_html_have_doctype(self, all_html_files):
        """All HTML files must have DOCTYPE declaration."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert content.strip().startswith("<!DOCTYPE html>"), \
                f"{html_file.name} missing DOCTYPE"

    def test_all_html_have_charset(self, all_html_files):
        """All HTML files must declare UTF-8 charset."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            assert 'charset="utf-8"' in content_lower or "charset=utf-8" in content_lower, \
                f"{html_file.name} missing charset"

    def test_all_html_have_viewport(self, all_html_files):
        """All HTML files must have viewport meta tag."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert "viewport" in content, f"{html_file.name} missing viewport"

    def test_all_html_have_csp(self, all_html_files):
        """All HTML files must have CSP meta tag."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert re.search(CSP_PATTERN, content), \
                f"{html_file.name} missing CSP meta tag"


class TestExternalAssetNegative:
    """Security negative tests: ensure no external dependencies in any docs file."""

    @pytest.fixture
    def all_html_files(self) -> list[Path]:
        """Get all HTML files in docs/modules."""
        if not DOCS_DIR.exists():
            pytest.skip("docs/modules directory does not exist")
        return list(DOCS_DIR.glob("*.html"))

    def test_no_external_scripts(self, all_html_files):
        """No HTML file should reference external scripts."""
        pattern = r'<script[^>]+src="https?://'
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert not matches, f"{html_file.name} has external script: {matches}"

    def test_no_external_stylesheets(self, all_html_files):
        """No HTML file should reference external stylesheets."""
        pattern = r'<link[^>]+href="https?://'
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert not matches, f"{html_file.name} has external stylesheet: {matches}"

    def test_no_css_imports(self, all_html_files):
        """No HTML file should have @import with external URLs."""
        pattern = r'@import\s+["\']https?://'
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert not matches, f"{html_file.name} has external @import: {matches}"

    def test_no_external_fonts(self, all_html_files):
        """No HTML file should load external fonts (privacy concern)."""
        patterns = [
            r'fonts\.googleapis\.com',
            r'fonts\.gstatic\.com',
            r'use\.typekit\.net',
        ]
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert not matches, f"{html_file.name} loads external fonts: {pattern}"


class TestJSAssetFiles:
    """Tests for JavaScript asset files in docs/modules/assets/."""

    @pytest.fixture
    def assets_dir(self) -> Path:
        """Get assets directory."""
        return DOCS_DIR / "assets"

    def test_theme_js_exists(self, assets_dir):
        """theme.js must exist in assets directory."""
        assert (assets_dir / "theme.js").exists()

    def test_highlight_js_exists(self, assets_dir):
        """highlight.js must exist in assets directory."""
        assert (assets_dir / "highlight.js").exists()

    def test_theme_js_no_external_fetch(self, assets_dir):
        """theme.js must not fetch external resources."""
        content = (assets_dir / "theme.js").read_text(encoding="utf-8")
        assert "fetch('http" not in content
        assert 'fetch("http' not in content
        assert "XMLHttpRequest" not in content

    def test_highlight_js_no_external_fetch(self, assets_dir):
        """highlight.js must not fetch external resources."""
        content = (assets_dir / "highlight.js").read_text(encoding="utf-8")
        assert "fetch('http" not in content
        assert 'fetch("http' not in content
        assert "XMLHttpRequest" not in content
