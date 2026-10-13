"""Tests for generated module documentation HTML files."""

import re
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).parent.parent / "docs" / "modules"

# Patterns that indicate external resources (should NOT be present)
EXTERNAL_PATTERNS = [
    r'href="https?://',
    r'src="https?://',
    r'url\(["\']?https?://',
    r'@import\s+["\']https?://',
]

# Required headings for module docs
REQUIRED_HEADINGS = ["Purpose", "Validation", "Example"]

# CSP meta tag pattern
CSP_PATTERN = r'<meta\s+http-equiv="Content-Security-Policy"'


class TestConfigModuleDocs:
    """Tests for config module documentation."""

    @pytest.fixture
    def config_html(self) -> str:
        """Load config.html content."""
        path = DOCS_DIR / "config.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    @pytest.fixture
    def config_side_by_side_html(self) -> str:
        """Load config_side_by_side.html content."""
        path = DOCS_DIR / "config_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_config_html_no_external_assets(self, config_html):
        """config.html should have no external asset references."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, config_html, re.IGNORECASE)
            assert not matches, f"Found external reference: {pattern}"

    def test_config_html_has_csp(self, config_html):
        """config.html should have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, config_html), "Missing CSP meta tag"

    def test_config_html_has_required_headings(self, config_html):
        """config.html should have required documentation headings."""
        for heading in REQUIRED_HEADINGS:
            assert heading.lower() in config_html.lower(), f"Missing heading: {heading}"

    def test_config_html_has_threshold_docs(self, config_html):
        """config.html should document threshold semantics."""
        assert "indifference" in config_html.lower()
        assert "preference" in config_html.lower()
        assert "veto" in config_html.lower()

    def test_config_side_by_side_no_external_assets(self, config_side_by_side_html):
        """config_side_by_side.html should have no external asset references."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, config_side_by_side_html, re.IGNORECASE)
            assert not matches, f"Found external reference: {pattern}"

    def test_config_side_by_side_has_csp(self, config_side_by_side_html):
        """config_side_by_side.html should have CSP meta tag."""
        assert re.search(CSP_PATTERN, config_side_by_side_html), "Missing CSP meta tag"

    def test_config_side_by_side_has_line_numbers(self, config_side_by_side_html):
        """config_side_by_side.html should have line numbers."""
        assert 'class="line-num"' in config_side_by_side_html

    def test_config_side_by_side_has_pane_structure(self, config_side_by_side_html):
        """config_side_by_side.html should have code and doc panes."""
        assert "pane-code" in config_side_by_side_html
        assert "pane-doc" in config_side_by_side_html

    def test_config_side_by_side_responsive(self, config_side_by_side_html):
        """config_side_by_side.html should have responsive CSS."""
        assert "@media" in config_side_by_side_html
        assert "900px" in config_side_by_side_html


class TestHTMLValidity:
    """Basic HTML validity tests."""

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
        """All HTML files should have DOCTYPE declaration."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert content.strip().startswith("<!DOCTYPE html>"), f"{html_file.name} missing DOCTYPE"

    def test_all_html_have_charset(self, all_html_files):
        """All HTML files should declare UTF-8 charset."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert 'charset="UTF-8"' in content or "charset=UTF-8" in content, f"{html_file.name} missing charset"

    def test_all_html_have_viewport(self, all_html_files):
        """All HTML files should have viewport meta tag."""
        for html_file in all_html_files:
            content = html_file.read_text(encoding="utf-8")
            assert "viewport" in content, f"{html_file.name} missing viewport"
