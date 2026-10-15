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


class TestConcordanceTutorialScaffold:
    """Tests for concordance_tutorial_side_by_side.html scaffold."""

    @pytest.fixture
    def concordance_html(self) -> str:
        """Load concordance_tutorial_side_by_side.html content."""
        path = DOCS_DIR / "concordance_tutorial_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """concordance_tutorial_side_by_side.html must exist."""
        path = DOCS_DIR / "concordance_tutorial_side_by_side.html"
        assert path.exists(), "Concordance tutorial file missing"

    def test_has_csp_meta_tag(self, concordance_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, concordance_html), "Missing CSP meta tag"

    def test_has_layout2_structure(self, concordance_html):
        """Tutorial must have Layout 2 structure elements."""
        assert 'class="shell"' in concordance_html, "Missing .shell grid"
        assert 'class="sidebar"' in concordance_html, "Missing .sidebar"
        assert 'class="rows"' in concordance_html, "Missing .rows container"

    def test_has_r1_through_r5_rows(self, concordance_html):
        """Tutorial must have rows R1-R5."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="row-{r}"' in concordance_html, f"Missing row id=row-{r}"

    def test_has_io_summary_section(self, concordance_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in concordance_html, "Missing .io-summary"
        assert "I/O Summary" in concordance_html, "Missing I/O Summary heading"

    def test_has_jump_navigation(self, concordance_html):
        """Tutorial must have sidebar jump navigation."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="jump-{r}"' in concordance_html, f"Missing jump id=jump-{r}"
            assert f'href="#row-{r}"' in concordance_html, f"Missing href=#row-{r}"

    def test_has_progress_indicator(self, concordance_html):
        """Tutorial must have progress indicator elements."""
        assert 'id="prog-txt"' in concordance_html, "Missing prog-txt element"
        assert 'id="prog-fill"' in concordance_html, "Missing prog-fill element"

    def test_has_theme_toggle(self, concordance_html):
        """Tutorial must have theme toggle segment."""
        assert 'class="seg"' in concordance_html, "Missing .seg theme toggle"
        assert 'data-theme-value="light"' in concordance_html
        assert 'data-theme-value="dark"' in concordance_html

    def test_references_js_assets(self, concordance_html):
        """Tutorial must reference theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in concordance_html, "Missing theme.js reference"
        assert 'src="assets/highlight.js"' in concordance_html, "Missing highlight.js reference"

    def test_each_row_has_required_subheadings(self, concordance_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert concordance_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert concordance_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert concordance_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert concordance_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, concordance_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, concordance_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_concordance_content(self, concordance_html):
        """Tutorial must have concordance-specific content."""
        assert "concordance" in concordance_html.lower()
        assert "partial_concordance" in concordance_html
        assert "global_concordance" in concordance_html


class TestDiscordanceTutorialScaffold:
    """Tests for discordance_tutorial_side_by_side.html scaffold."""

    @pytest.fixture
    def discordance_html(self) -> str:
        """Load discordance_tutorial_side_by_side.html content."""
        path = DOCS_DIR / "discordance_tutorial_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """discordance_tutorial_side_by_side.html must exist."""
        path = DOCS_DIR / "discordance_tutorial_side_by_side.html"
        assert path.exists(), "Discordance tutorial file missing"

    def test_has_csp_meta_tag(self, discordance_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, discordance_html), "Missing CSP meta tag"

    def test_has_layout2_structure(self, discordance_html):
        """Tutorial must have Layout 2 structure elements."""
        assert 'class="shell"' in discordance_html, "Missing .shell grid"
        assert 'class="sidebar"' in discordance_html, "Missing .sidebar"
        assert 'class="rows"' in discordance_html, "Missing .rows container"

    def test_has_r1_through_r5_rows(self, discordance_html):
        """Tutorial must have rows R1-R5."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="row-{r}"' in discordance_html, f"Missing row id=row-{r}"

    def test_has_io_summary_section(self, discordance_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in discordance_html, "Missing .io-summary"
        assert "I/O Summary" in discordance_html, "Missing I/O Summary heading"

    def test_has_jump_navigation(self, discordance_html):
        """Tutorial must have sidebar jump navigation."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="jump-{r}"' in discordance_html, f"Missing jump id=jump-{r}"
            assert f'href="#row-{r}"' in discordance_html, f"Missing href=#row-{r}"

    def test_has_progress_indicator(self, discordance_html):
        """Tutorial must have progress indicator elements."""
        assert 'id="prog-txt"' in discordance_html, "Missing prog-txt element"
        assert 'id="prog-fill"' in discordance_html, "Missing prog-fill element"

    def test_has_theme_toggle(self, discordance_html):
        """Tutorial must have theme toggle segment."""
        assert 'class="seg"' in discordance_html, "Missing .seg theme toggle"
        assert 'data-theme-value="light"' in discordance_html
        assert 'data-theme-value="dark"' in discordance_html

    def test_references_js_assets(self, discordance_html):
        """Tutorial must reference theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in discordance_html, "Missing theme.js reference"
        assert 'src="assets/highlight.js"' in discordance_html, "Missing highlight.js reference"

    def test_each_row_has_required_subheadings(self, discordance_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert discordance_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert discordance_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert discordance_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert discordance_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, discordance_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, discordance_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_discordance_content(self, discordance_html):
        """Tutorial must have discordance-specific content."""
        assert "discordance" in discordance_html.lower()
        assert "veto" in discordance_html.lower()
        assert "d_j" in discordance_html or "d_interp" in discordance_html

    def test_no_deterministic_output_assertions(self, discordance_html):
        """Tutorial must not have deterministic output assertions like '= 1.0 (veto triggered)'."""
        assert "= 1.0 (veto triggered)" not in discordance_html
        assert "= 0.0 (no discordance)" not in discordance_html
        # No exact array index output predictions
        assert "d_j[0,0,1] = 1.0" not in discordance_html
        assert "d_j[0,0,1] = 0.0" not in discordance_html

    def test_no_absolute_causal_language(self, discordance_html):
        """Tutorial must not use absolute causal language about veto/credibility effects."""
        content_lower = discordance_html.lower()
        # No 'regardless' absolute phrasing
        assert "regardless of concordance" not in content_lower
        assert "regardless of interpolation" not in content_lower
        # No strong causal language about d=1 effects
        assert "kills credibility" not in content_lower
        assert "drive s(a,b) toward 0" not in content_lower
        assert "attenuates concordance" not in content_lower
        # Should use conditional language instead (may, can, depends)

    def test_has_usage_disclaimer(self, discordance_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in discordance_html
        assert "illustrative" in discordance_html.lower()
        assert "do not treat" in discordance_html.lower()

    def test_output_card_marked_illustrative(self, discordance_html):
        """Output card must be marked as illustrative, not stdout."""
        # Should not have definitive stdout block without illustrative marker
        assert 'illustrative' in discordance_html

    def test_has_option3_grounding_facts_line(self, discordance_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in discordance_html, "Missing .gnd-facts container"
        assert "<dl>" in discordance_html, "Missing dl element for facts"
        assert "<dt>" in discordance_html, "Missing dt elements"
        assert "<dd>" in discordance_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, discordance_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in discordance_html, "Missing .gnd-details"
        assert "<details" in discordance_html, "Missing details element"
        assert "<summary>" in discordance_html, "Missing summary element"
        assert 'class="gnd-content"' in discordance_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, discordance_html):
        """Grounding facts must include key invariants."""
        # Facts line should have key invariants
        assert "Range" in discordance_html
        assert "[0,1]" in discordance_html
        assert "p &le; v" in discordance_html or "p ≤ v" in discordance_html
        # Expandable section should have Definition
        assert "Definition" in discordance_html

    def test_no_recommended_threshold_defaults(self, discordance_html):
        """Tutorial must not suggest specific threshold values as recommended."""
        # Should not suggest specific p/v values as recommendations
        assert "recommended p =" not in discordance_html.lower()
        assert "recommended v =" not in discordance_html.lower()
        assert "use p = " not in discordance_html.lower()
        assert "use v = " not in discordance_html.lower()
        # Disclaimer warning against treating examples as defaults is OK


class TestCredibilityTutorialScaffold:
    """Tests for credibility_tutorial_side_by_side.html scaffold with Option 3 layout."""

    @pytest.fixture
    def credibility_html(self) -> str:
        """Load credibility_tutorial_side_by_side.html content."""
        path = DOCS_DIR / "credibility_tutorial_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """credibility_tutorial_side_by_side.html must exist."""
        path = DOCS_DIR / "credibility_tutorial_side_by_side.html"
        assert path.exists(), "Credibility tutorial file missing"

    def test_has_csp_meta_tag(self, credibility_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, credibility_html), "Missing CSP meta tag"

    def test_has_layout2_structure(self, credibility_html):
        """Tutorial must have Layout 2 structure elements."""
        assert 'class="shell"' in credibility_html, "Missing .shell grid"
        assert 'class="sidebar"' in credibility_html, "Missing .sidebar"
        assert 'class="rows"' in credibility_html, "Missing .rows container"

    def test_has_r1_through_r5_rows(self, credibility_html):
        """Tutorial must have rows R1-R5."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="row-{r}"' in credibility_html, f"Missing row id=row-{r}"

    def test_has_io_summary_section(self, credibility_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in credibility_html, "Missing .io-summary"
        assert "I/O Summary" in credibility_html, "Missing I/O Summary heading"

    def test_has_jump_navigation(self, credibility_html):
        """Tutorial must have sidebar jump navigation."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="jump-{r}"' in credibility_html, f"Missing jump id=jump-{r}"

    def test_has_progress_indicator(self, credibility_html):
        """Tutorial must have progress indicator elements."""
        assert 'id="prog-txt"' in credibility_html, "Missing prog-txt element"
        assert 'id="prog-fill"' in credibility_html, "Missing prog-fill element"

    def test_references_js_assets(self, credibility_html):
        """Tutorial must reference only theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in credibility_html, "Missing theme.js reference"
        assert 'src="assets/highlight.js"' in credibility_html, "Missing highlight.js reference"

    def test_each_row_has_required_subheadings(self, credibility_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert credibility_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert credibility_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert credibility_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert credibility_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, credibility_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, credibility_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_credibility_content(self, credibility_html):
        """Tutorial must have credibility-specific content."""
        assert "credibility" in credibility_html.lower()
        assert "S(a,b)" in credibility_html or "S_ab" in credibility_html
        assert "concordance" in credibility_html.lower()

    def test_has_option3_grounding_facts_line(self, credibility_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in credibility_html, "Missing .gnd-facts container"
        assert "<dl>" in credibility_html, "Missing dl element for facts"
        assert "<dt>" in credibility_html, "Missing dt elements"
        assert "<dd>" in credibility_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, credibility_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in credibility_html, "Missing .gnd-details"
        assert "<details" in credibility_html, "Missing details element"
        assert "<summary>" in credibility_html, "Missing summary element"
        assert 'class="gnd-content"' in credibility_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, credibility_html):
        """Grounding facts must include key invariants."""
        assert "Range" in credibility_html
        assert "[0,1]" in credibility_html
        assert "Diagonal" in credibility_html
        assert "Definition" in credibility_html

    def test_uses_implementation_contract_wording(self, credibility_html):
        """Tutorial must use implementation contract wording, not vague 'typically'."""
        # Should use clips/implementation language
        assert "clips output to [0,1]" in credibility_html
        # Should NOT use vague 'typically fall' language
        assert "typically fall in [0,1]" not in credibility_html

    def test_diagonal_not_enforced_here_wording(self, credibility_html):
        """Tutorial must clarify diagonal is not enforced by this function."""
        # Should clarify diagonal handled upstream, not enforced here
        assert "not enforce" in credibility_html.lower() or "does not enforce" in credibility_html.lower()
        # Should NOT claim S(a,a)=0 is guaranteed/set by this function
        assert "S(a,a) = 0 (set upstream)" not in credibility_html

    def test_no_deterministic_output_assertions(self, credibility_html):
        """Tutorial must not have deterministic output assertions."""
        assert "= 0.8 (" not in credibility_html
        assert "= 1.0 (" not in credibility_html
        assert "S[0,0] =" not in credibility_html

    def test_has_usage_disclaimer(self, credibility_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in credibility_html
        assert "illustrative" in credibility_html.lower()
        assert "do not treat" in credibility_html.lower()
