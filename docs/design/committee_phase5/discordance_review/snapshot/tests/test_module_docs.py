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


def assert_style_standard_v1(html: str) -> None:
    """Shared assertion for dark mode readability + Variant B selection style standard."""
    # Dark mode readability tokens
    assert "--note-text:" in html, "Missing --note-text token"
    assert "--note-size:" in html, "Missing --note-size token"
    assert "--h4-color:" in html, "Missing --h4-color token"
    assert "--h4-border:" in html, "Missing --h4-border token"
    # Variant B selection tokens
    assert "--sel-accent:" in html, "Missing --sel-accent token"
    assert "--sel-soft:" in html, "Missing --sel-soft token"
    assert "--sel-border:" in html, "Missing --sel-border token"
    # Selection uses tokens (not hardcoded accent)
    assert ".row.sel" in html, "Missing .row.sel styles"
    assert '"selected"' in html or "'selected'" in html, "Missing 'selected' non-color cue"


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

    def test_has_style_standard_v1(self, tutorial_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(tutorial_html)

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

    def test_has_style_standard_v1(self, concordance_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(concordance_html)

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

    # === Deep content tests (C1) ===

    def test_has_option3_grounding_facts(self, concordance_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in concordance_html, "Missing .gnd-facts container"
        assert "<dl" in concordance_html, "Missing dl element for facts"
        assert "<dt" in concordance_html, "Missing dt elements"
        assert "<dd" in concordance_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, concordance_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in concordance_html or "<details" in concordance_html, "Missing expandable details"
        assert "<summary" in concordance_html, "Missing summary element"

    def test_r1_has_substantive_content(self, concordance_html):
        """R1 must have substantive content about concordance role in ELECTRE III."""
        # Must mention the three-stage pipeline
        assert "discordance" in concordance_html.lower(), "R1 should mention discordance"
        assert "credibility" in concordance_html.lower(), "R1 should mention credibility"
        # Must mention coalition/support concept
        assert "coalition" in concordance_html.lower() or "support" in concordance_html.lower()

    def test_r2_has_piecewise_formula_content(self, concordance_html):
        """R2 must have piecewise formula content with q and p thresholds."""
        # Must mention piecewise
        assert "piecewise" in concordance_html.lower()
        # Must mention indifference and preference thresholds
        assert "indifference" in concordance_html.lower()
        assert "preference" in concordance_html.lower()
        # Must mention the boundary conditions
        assert "-q" in concordance_html or "&minus;q" in concordance_html.lower()
        assert "-p" in concordance_html or "&minus;p" in concordance_html.lower()

    def test_r2_mentions_maximize_minimize(self, concordance_html):
        """R2 should note maximize vs minimize semantics."""
        assert "maximize" in concordance_html.lower() or "minimize" in concordance_html.lower()

    def test_r3_has_implementation_details(self, concordance_html):
        """R3 must have implementation details about vectorization and clipping."""
        assert "vectoriz" in concordance_html.lower() or "broadcast" in concordance_html.lower()
        assert "clip" in concordance_html.lower()
        assert "monoton" in concordance_html.lower(), "Should mention monotonicity"

    def test_r4_has_weight_normalization_content(self, concordance_html):
        """R4 must explain weight normalization contract."""
        assert "normalize" in concordance_html.lower()
        assert "sum" in concordance_html.lower() and ("weights" in concordance_html.lower() or "= 1" in concordance_html)
        assert "einsum" in concordance_html.lower(), "Should mention einsum implementation"

    def test_r4_weights_nonnegative_requirement(self, concordance_html):
        """R4 must require weights >= 0."""
        # Check for non-negative weights requirement
        assert "weights" in concordance_html.lower() and (
            "&ge; 0" in concordance_html or ">= 0" in concordance_html or "≥ 0" in concordance_html
        ), "Must require weights >= 0"

    def test_r4_upstream_enforcement(self, concordance_html):
        """R4 must clarify that normalize_weights enforcement is upstream-only."""
        lower = concordance_html.lower()
        assert "upstream" in lower, "Must mention upstream enforcement"
        assert "not enforced" in lower or "does not validate" in lower, "Must clarify not enforced in this module"

    def test_r3_qp_masked_wording(self, concordance_html):
        """R3 must use 'masked' wording for q=p case, not 'never used'."""
        lower = concordance_html.lower()
        # Should NOT say "never used"
        assert "never used" not in lower, "Should not say 'never used' for c_interp"
        # Should say "masked" or similar
        assert "masked" in lower, "Should say c_interp is 'masked' by piecewise branches"

    def test_r5_has_edge_cases_content(self, concordance_html):
        """R5 must have edge cases: NaN/Inf, criteria mismatch, q=p degeneracy."""
        lower = concordance_html.lower()
        assert "nan" in lower or "NaN" in concordance_html, "Should mention NaN handling"
        assert "q=p" in concordance_html or "q equals p" in lower or "degener" in lower, "Should mention q=p degeneracy"
        assert "mismatch" in lower or "criteria" in lower, "Should mention criteria mismatch"

    def test_io_summary_has_shapes_and_invariants(self, concordance_html):
        """I/O Summary must include shapes and invariants."""
        # Check for shape notation
        assert "B1,B2,C" in concordance_html or "B1, B2, C" in concordance_html
        assert "ndarray" in concordance_html.lower()
        # Check for invariant/precondition language
        assert "invariant" in concordance_html.lower() or "precondition" in concordance_html.lower()

    def test_has_usage_disclaimer(self, concordance_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in concordance_html or "usage-disclaimer" in concordance_html
        assert "illustrative" in concordance_html.lower()

    def test_no_deterministic_output_assertions(self, concordance_html):
        """Tutorial must not have deterministic output assertions."""
        # Should not claim specific numeric outputs
        assert "c_j[0] =" not in concordance_html
        assert "C[0,1] =" not in concordance_html
        assert "expected c_j" not in concordance_html.lower()
        assert "expected concordance" not in concordance_html.lower()

    def test_no_unqualified_speedup_claims(self, concordance_html):
        """Tutorial must not make unqualified speedup claims."""
        lower = concordance_html.lower()
        # If "faster" or "speedup" mentioned, must be qualified
        if "faster" in lower or "speedup" in lower:
            assert "typically" in lower or "may be" in lower or "qualified" in lower or "memory" in lower, \
                "Speedup claims must be qualified"

    def test_grounding_mentions_electre_context(self, concordance_html):
        """Grounding section must mention ELECTRE III context."""
        assert "ELECTRE" in concordance_html
        # Should explain the three-pillar structure
        assert "concordance" in concordance_html.lower() and "discordance" in concordance_html.lower()

    # === Notation and shape clarification tests (C1-fix1) ===

    def test_has_notation_block(self, concordance_html):
        """Tutorial must have Notation block defining B1, B2, C, N."""
        assert "Notation" in concordance_html, "Missing Notation heading"
        # Must define the key dimension variables
        lower = concordance_html.lower()
        assert "b1" in lower and "b2" in lower, "Notation must define B1 and B2"
        assert "number of alternatives" in lower or "alternatives" in lower
        assert "number of criteria" in lower or "criteria" in lower

    def test_notation_explains_g_function(self, concordance_html):
        """Notation must explain g(a,j) performance function."""
        assert "g(a" in concordance_html.lower() or "g(a,j)" in concordance_html, "Must explain g(a,j)"
        assert "performance" in concordance_html.lower()

    def test_explains_diff_shape_with_example(self, concordance_html):
        """Tutorial must explain diff shape (B1,B2,C) with triple-bracket example."""
        # Must explain the triple bracket structure
        assert "[[[" in concordance_html, "Must include triple-bracket example like [[[d1,d2,d3]]]"
        # Must explain what each bracket level means
        lower = concordance_html.lower()
        assert "row" in lower and "col" in lower, "Must explain row/column dimensions"

    def test_example_clarifies_alts_terminology(self, concordance_html):
        """Usage example must clarify 'alts' means alternatives."""
        # The example comment should explain the terminology
        assert "alternative" in concordance_html.lower(), "Should use full word 'alternative'"
        # Should show the shape explicitly
        assert "B1=" in concordance_html or "B1=1" in concordance_html, "Should show B1 dimension in example"


class TestDiscordanceDeepTutorial:
    """Structure and content checks for the deep discordance tutorial."""

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

    def test_has_style_standard_v1(self, discordance_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(discordance_html)

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

    def test_verified_example_and_precise_veto_contract(self, discordance_html):
        """Verified numeric examples are allowed; faux stdout claims are not."""
        assert 'id="scenario-results"' in discordance_html
        assert 'id="example"' in discordance_html
        assert 'stdout' not in discordance_html and '~0.1 ms' not in discordance_html
        assert '[Placeholder]' not in discordance_html
        assert 'full-veto rule in credibility() sets S=0' in discordance_html
        assert 'p=v' in discordance_html and 'veto-first' in discordance_html

    def test_has_usage_disclaimer(self, discordance_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in discordance_html
        assert "illustrative" in discordance_html.lower()
        assert "do not treat" in discordance_html.lower()

    def test_example_inputs_marked_illustrative(self, discordance_html):
        """The actual worked example contains an adjacent input disclaimer."""
        example = discordance_html.split('id="example"', 1)[1].split('</details>', 1)[0]
        assert 'class="usage-disclaimer"' in example
        assert 'illustrative example inputs only' in example.lower()
        assert 'specified inputs' in example

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

    def test_has_style_standard_v1(self, credibility_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(credibility_html)

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


class TestRankingTutorialScaffold:
    """Tests for ranking_tutorial_side_by_side.html scaffold with Option 3 layout."""

    @pytest.fixture
    def ranking_html(self) -> str:
        """Load ranking_tutorial_side_by_side.html content."""
        path = DOCS_DIR / "ranking_tutorial_side_by_side.html"
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """ranking_tutorial_side_by_side.html must exist."""
        path = DOCS_DIR / "ranking_tutorial_side_by_side.html"
        assert path.exists(), "Ranking tutorial file missing"

    def test_has_csp_meta_tag(self, ranking_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert re.search(CSP_PATTERN, ranking_html), "Missing CSP meta tag"

    def test_has_style_standard_v1(self, ranking_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(ranking_html)

    def test_has_layout2_structure(self, ranking_html):
        """Tutorial must have Layout 2 structure elements."""
        assert 'class="shell"' in ranking_html, "Missing .shell grid"
        assert 'class="sidebar"' in ranking_html, "Missing .sidebar"
        assert 'class="rows"' in ranking_html, "Missing .rows container"

    def test_has_r1_through_r5_rows(self, ranking_html):
        """Tutorial must have rows R1-R5."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="row-{r}"' in ranking_html, f"Missing row id=row-{r}"

    def test_has_io_summary_section(self, ranking_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in ranking_html, "Missing .io-summary"
        assert "I/O Summary" in ranking_html, "Missing I/O Summary heading"

    def test_has_jump_navigation(self, ranking_html):
        """Tutorial must have sidebar jump navigation."""
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="jump-{r}"' in ranking_html, f"Missing jump id=jump-{r}"

    def test_has_progress_indicator(self, ranking_html):
        """Tutorial must have progress indicator elements."""
        assert 'id="prog-txt"' in ranking_html, "Missing prog-txt element"
        assert 'id="prog-fill"' in ranking_html, "Missing prog-fill element"

    def test_references_js_assets(self, ranking_html):
        """Tutorial must reference only theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in ranking_html, "Missing theme.js reference"
        assert 'src="assets/highlight.js"' in ranking_html, "Missing highlight.js reference"

    def test_each_row_has_required_subheadings(self, ranking_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert ranking_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert ranking_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert ranking_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert ranking_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, ranking_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, ranking_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_ranking_content(self, ranking_html):
        """Tutorial must have ranking-specific content."""
        assert "compute_ranking" in ranking_html
        assert "NetFlowAccumulator" in ranking_html
        assert "net_flow" in ranking_html.lower() or "net flow" in ranking_html.lower()

    def test_has_option3_grounding_facts_line(self, ranking_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in ranking_html, "Missing .gnd-facts container"
        assert "<dl>" in ranking_html, "Missing dl element for facts"
        assert "<dt>" in ranking_html, "Missing dt elements"
        assert "<dd>" in ranking_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, ranking_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in ranking_html, "Missing .gnd-details"
        assert "<details" in ranking_html, "Missing details element"
        assert "<summary>" in ranking_html, "Missing summary element"
        assert 'class="gnd-content"' in ranking_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, ranking_html):
        """Grounding facts must include key invariants."""
        assert "Criteria" in ranking_html
        assert "non-empty" in ranking_html.lower()
        assert "Diagonal" in ranking_html
        assert "Memory" in ranking_html

    def test_no_deterministic_output_assertions(self, ranking_html):
        """Tutorial must not have deterministic output assertions."""
        assert "ranking[0] =" not in ranking_html
        assert "= [0, 1, 2]" not in ranking_html
        assert "expected ranking" not in ranking_html.lower()

    def test_no_seed_mention(self, ranking_html):
        """Tutorial must not mention seed since ranking.py does not use it."""
        assert "seed" not in ranking_html.lower()

    def test_no_phi_norm_reference(self, ranking_html):
        """Tutorial must not reference phi_norm unless code computes it."""
        assert "phi_norm" not in ranking_html

    def test_no_electre_iii_ii_typo(self, ranking_html):
        """Tutorial must not have 'ELECTRE III II' typo."""
        assert "ELECTRE III II" not in ranking_html

    def test_has_usage_disclaimer(self, ranking_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in ranking_html
        assert "illustrative" in ranking_html.lower()
        assert "do not treat" in ranking_html.lower()


class TestValidateTutorialScaffold:
    """Tests for validate_tutorial_side_by_side.html scaffold."""

    @pytest.fixture
    def validate_html(self):
        """Load validate tutorial HTML."""
        path = DOCS_DIR / "validate_tutorial_side_by_side.html"
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """Validate tutorial file must exist."""
        path = DOCS_DIR / "validate_tutorial_side_by_side.html"
        assert path.exists(), f"Missing file: {path}"

    def test_has_doctype(self, validate_html):
        """Tutorial must have HTML5 doctype."""
        assert validate_html.strip().startswith("<!DOCTYPE html>")

    def test_has_csp_meta(self, validate_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert 'http-equiv="Content-Security-Policy"' in validate_html
        assert "script-src 'self'" in validate_html

    def test_has_shell_structure(self, validate_html):
        """Tutorial must have Layout2 .shell structure."""
        assert 'class="shell"' in validate_html

    def test_has_sidebar(self, validate_html):
        """Tutorial must have .sidebar element."""
        assert 'class="sidebar"' in validate_html

    def test_has_rows_container(self, validate_html):
        """Tutorial must have .rows container."""
        assert 'class="rows"' in validate_html

    def test_has_five_range_rows(self, validate_html):
        """Tutorial must have 5 range rows (R1-R5)."""
        assert 'id="row-R1"' in validate_html
        assert 'id="row-R2"' in validate_html
        assert 'id="row-R3"' in validate_html
        assert 'id="row-R4"' in validate_html
        assert 'id="row-R5"' in validate_html

    def test_has_jump_navigation(self, validate_html):
        """Tutorial must have jump-to navigation for R1-R5."""
        assert 'href="#row-R1"' in validate_html
        assert 'href="#row-R2"' in validate_html
        assert 'href="#row-R3"' in validate_html
        assert 'href="#row-R4"' in validate_html
        assert 'href="#row-R5"' in validate_html

    def test_has_theme_toggle(self, validate_html):
        """Tutorial must have theme toggle buttons."""
        assert 'data-theme-value="light"' in validate_html
        assert 'data-theme-value="dark"' in validate_html
        assert 'data-theme-value="system"' in validate_html

    def test_has_progress_indicator(self, validate_html):
        """Tutorial must have progress indicator."""
        assert 'id="prog-indicator"' in validate_html or 'class="prog"' in validate_html

    def test_references_local_scripts(self, validate_html):
        """Tutorial must reference only theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in validate_html
        assert 'src="assets/highlight.js"' in validate_html

    def test_each_row_has_required_subheadings(self, validate_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert validate_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert validate_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert validate_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert validate_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, validate_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, validate_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_validate_content(self, validate_html):
        """Tutorial must have validate-specific content."""
        assert "validate_matrix" in validate_html
        assert "normalize_weights" in validate_html
        assert "validate_arrays_match" in validate_html
        assert "validate_thresholds" in validate_html

    def test_has_option3_grounding_facts_line(self, validate_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in validate_html, "Missing .gnd-facts container"
        assert "<dl>" in validate_html, "Missing dl element for facts"
        assert "<dt>" in validate_html, "Missing dt elements"
        assert "<dd>" in validate_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, validate_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in validate_html, "Missing .gnd-details"
        assert "<details" in validate_html, "Missing details element"
        assert "<summary>" in validate_html, "Missing summary element"
        assert 'class="gnd-content"' in validate_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, validate_html):
        """Grounding facts must include key invariants."""
        assert "2D" in validate_html or "2-D" in validate_html
        assert "finite" in validate_html.lower()
        assert "sum = 1" in validate_html or "sum=1" in validate_html

    def test_no_deterministic_output_assertions(self, validate_html):
        """Tutorial must not have deterministic output assertions."""
        assert "weights[0] =" not in validate_html
        assert "= [0.5, 0.5]" not in validate_html
        assert "expected weights" not in validate_html.lower()

    def test_has_io_summary(self, validate_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in validate_html
        assert "I/O Summary" in validate_html

    def test_has_usage_disclaimer(self, validate_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in validate_html
        assert "illustrative" in validate_html.lower()
        assert "do not treat" in validate_html.lower()

    def test_mentions_fail_fast(self, validate_html):
        """Tutorial should mention fail-fast philosophy."""
        assert "fail-fast" in validate_html.lower() or "fail fast" in validate_html.lower()

    def test_mentions_valueerror(self, validate_html):
        """Tutorial must mention ValueError as the exception type."""
        assert "ValueError" in validate_html

    # Dark mode readability tests
    def test_has_dark_mode_note_text_token(self, validate_html):
        """Tutorial must have --note-text CSS token for dark mode readability."""
        assert "--note-text:" in validate_html

    def test_has_dark_mode_note_size_token(self, validate_html):
        """Tutorial must have --note-size CSS token for dark mode text sizing."""
        assert "--note-size:" in validate_html

    def test_has_dark_mode_h4_color_token(self, validate_html):
        """Tutorial must have --h4-color CSS token for header contrast."""
        assert "--h4-color:" in validate_html

    def test_has_dark_mode_h4_border_token(self, validate_html):
        """Tutorial must have --h4-border CSS token for green accent."""
        assert "--h4-border:" in validate_html

    def test_note_col_uses_note_text_token(self, validate_html):
        """Note column must use --note-text token for text color."""
        assert "color:var(--note-text)" in validate_html

    def test_note_col_uses_note_size_token(self, validate_html):
        """Note column must use --note-size token for font size."""
        assert "font-size:var(--note-size)" in validate_html

    def test_h4_uses_h4_color_token(self, validate_html):
        """H4 headers must use --h4-color token."""
        assert "color:var(--h4-color)" in validate_html

    def test_h4_has_border_left(self, validate_html):
        """H4 headers must have border-left for green accent mark."""
        assert "border-left:" in validate_html and "--h4-border" in validate_html

    # Variant B selection highlight tests
    def test_has_selection_accent_token(self, validate_html):
        """Tutorial must have --sel-accent CSS token for green selection."""
        assert "--sel-accent:" in validate_html

    def test_has_selection_soft_token(self, validate_html):
        """Tutorial must have --sel-soft CSS token for selection background."""
        assert "--sel-soft:" in validate_html

    def test_has_selection_border_token(self, validate_html):
        """Tutorial must have --sel-border CSS token for selection border."""
        assert "--sel-border:" in validate_html

    def test_has_row_sel_styles(self, validate_html):
        """Tutorial must have .row.sel selection styles."""
        assert ".row.sel" in validate_html

    def test_selection_has_non_color_cue(self, validate_html):
        """Selection must have non-color cue (text chip 'selected')."""
        assert '"selected"' in validate_html or "'selected'" in validate_html

    def test_hl_uses_selection_tokens(self, validate_html):
        """Code highlight (.hl) must use selection tokens."""
        assert ".hl{" in validate_html or ".hl {" in validate_html
        assert "--sel-soft" in validate_html
        assert "--sel-accent" in validate_html


class TestBlockTutorialScaffold:
    """Tests for block_tutorial_side_by_side.html scaffold."""

    @pytest.fixture
    def block_html(self):
        """Load block tutorial HTML."""
        path = DOCS_DIR / "block_tutorial_side_by_side.html"
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """Block tutorial file must exist."""
        path = DOCS_DIR / "block_tutorial_side_by_side.html"
        assert path.exists(), f"Missing file: {path}"

    def test_has_doctype(self, block_html):
        """Tutorial must have HTML5 doctype."""
        assert block_html.strip().startswith("<!DOCTYPE html>")

    def test_has_csp_meta(self, block_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert 'http-equiv="Content-Security-Policy"' in block_html
        assert "script-src 'self'" in block_html

    def test_has_style_standard_v1(self, block_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(block_html)

    def test_has_shell_structure(self, block_html):
        """Tutorial must have Layout2 .shell structure."""
        assert 'class="shell"' in block_html

    def test_has_sidebar(self, block_html):
        """Tutorial must have .sidebar element."""
        assert 'class="sidebar"' in block_html

    def test_has_rows_container(self, block_html):
        """Tutorial must have .rows container."""
        assert 'class="rows"' in block_html

    def test_has_five_range_rows(self, block_html):
        """Tutorial must have 5 range rows (R1-R5)."""
        assert 'id="row-R1"' in block_html
        assert 'id="row-R2"' in block_html
        assert 'id="row-R3"' in block_html
        assert 'id="row-R4"' in block_html
        assert 'id="row-R5"' in block_html

    def test_has_jump_navigation(self, block_html):
        """Tutorial must have jump-to navigation for R1-R5."""
        assert 'href="#row-R1"' in block_html
        assert 'href="#row-R2"' in block_html
        assert 'href="#row-R3"' in block_html
        assert 'href="#row-R4"' in block_html
        assert 'href="#row-R5"' in block_html

    def test_has_theme_toggle(self, block_html):
        """Tutorial must have theme toggle buttons."""
        assert 'data-theme-value="light"' in block_html
        assert 'data-theme-value="dark"' in block_html
        assert 'data-theme-value="system"' in block_html

    def test_has_progress_indicator(self, block_html):
        """Tutorial must have progress indicator."""
        assert 'id="prog-indicator"' in block_html or 'class="prog"' in block_html

    def test_references_local_scripts(self, block_html):
        """Tutorial must reference only theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in block_html
        assert 'src="assets/highlight.js"' in block_html

    def test_each_row_has_required_subheadings(self, block_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert block_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert block_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert block_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert block_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, block_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, block_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_block_content(self, block_html):
        """Tutorial must have block-specific content."""
        assert "compute_block" in block_html
        assert "G_rows" in block_html
        assert "G_cols" in block_html
        assert "is_diagonal" in block_html

    def test_has_option3_grounding_facts_line(self, block_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in block_html, "Missing .gnd-facts container"
        assert "<dl>" in block_html, "Missing dl element for facts"
        assert "<dt>" in block_html, "Missing dt elements"
        assert "<dd>" in block_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, block_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in block_html, "Missing .gnd-details"
        assert "<details" in block_html, "Missing details element"
        assert "<summary>" in block_html, "Missing summary element"
        assert 'class="gnd-content"' in block_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, block_html):
        """Grounding facts must include key invariants."""
        assert "Diagonal" in block_html
        assert "[0,1]" in block_html or "0,1" in block_html
        assert "B1" in block_html and "B2" in block_html

    def test_no_deterministic_output_assertions(self, block_html):
        """Tutorial must not have deterministic output assertions."""
        assert "S[0,1] =" not in block_html
        assert "expected S" not in block_html.lower()

    def test_has_io_summary(self, block_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in block_html
        assert "I/O Summary" in block_html

    def test_has_usage_disclaimer(self, block_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in block_html
        assert "illustrative" in block_html.lower()
        assert "do not treat" in block_html.lower()

    def test_mentions_concordance_discordance_credibility(self, block_html):
        """Tutorial must mention integrated modules."""
        assert "concordance" in block_html.lower()
        assert "discordance" in block_html.lower()
        assert "credibility" in block_html.lower()

    def test_has_preconditions_wording(self, block_html):
        """Tutorial must label shape requirements as preconditions."""
        assert "Preconditions" in block_html or "precondition" in block_html.lower()
        assert "not enforced here" in block_html.lower()

    def test_has_min_b1_b2_diagonal_wording(self, block_html):
        """Tutorial must clarify diagonal zeros min(B1,B2) elements."""
        assert "min(B1,B2)" in block_html

    def test_has_mismatch_silently_mis_compute_wording(self, block_html):
        """Tutorial must warn about silent mis-compute on C mismatch."""
        assert "silently mis-compute" in block_html or "may error" in block_html

    def test_clipping_attributed_to_credibility_stage(self, block_html):
        """Tutorial must attribute clipping to credibility stage, not compute_block."""
        assert "credibility stage" in block_html.lower() or "clipped in credibility" in block_html.lower()

    def test_no_misleading_guarantee_phrases(self, block_html):
        """Tutorial must not claim compute_block guarantees or enforces shapes."""
        assert "compute_block guarantees" not in block_html.lower()
        assert "compute_block enforces" not in block_html.lower()
        assert "enforces shapes" not in block_html.lower()


class TestAccumulatorTutorialScaffold:
    """Tests for accumulator_tutorial_side_by_side.html scaffold."""

    @pytest.fixture
    def accumulator_html(self):
        """Load accumulator tutorial HTML."""
        path = DOCS_DIR / "accumulator_tutorial_side_by_side.html"
        return path.read_text(encoding="utf-8")

    def test_file_exists(self):
        """Accumulator tutorial file must exist."""
        path = DOCS_DIR / "accumulator_tutorial_side_by_side.html"
        assert path.exists(), f"Missing file: {path}"

    def test_has_doctype(self, accumulator_html):
        """Tutorial must have HTML5 doctype."""
        assert accumulator_html.strip().startswith("<!DOCTYPE html>")

    def test_has_csp_meta(self, accumulator_html):
        """Tutorial must have Content-Security-Policy meta tag."""
        assert 'http-equiv="Content-Security-Policy"' in accumulator_html
        assert "script-src 'self'" in accumulator_html

    def test_has_style_standard_v1(self, accumulator_html):
        """Tutorial must have dark mode readability + Variant B selection style standard."""
        assert_style_standard_v1(accumulator_html)

    def test_has_shell_structure(self, accumulator_html):
        """Tutorial must have Layout2 .shell structure."""
        assert 'class="shell"' in accumulator_html

    def test_has_sidebar(self, accumulator_html):
        """Tutorial must have .sidebar element."""
        assert 'class="sidebar"' in accumulator_html

    def test_has_rows_container(self, accumulator_html):
        """Tutorial must have .rows container."""
        assert 'class="rows"' in accumulator_html

    def test_has_five_range_rows(self, accumulator_html):
        """Tutorial must have 5 range rows (R1-R5)."""
        assert 'id="row-R1"' in accumulator_html
        assert 'id="row-R2"' in accumulator_html
        assert 'id="row-R3"' in accumulator_html
        assert 'id="row-R4"' in accumulator_html
        assert 'id="row-R5"' in accumulator_html

    def test_has_jump_navigation(self, accumulator_html):
        """Tutorial must have jump-to navigation for R1-R5."""
        assert 'href="#row-R1"' in accumulator_html
        assert 'href="#row-R2"' in accumulator_html
        assert 'href="#row-R3"' in accumulator_html
        assert 'href="#row-R4"' in accumulator_html
        assert 'href="#row-R5"' in accumulator_html

    def test_has_theme_toggle(self, accumulator_html):
        """Tutorial must have theme toggle buttons."""
        assert 'data-theme-value="light"' in accumulator_html
        assert 'data-theme-value="dark"' in accumulator_html
        assert 'data-theme-value="system"' in accumulator_html

    def test_has_progress_indicator(self, accumulator_html):
        """Tutorial must have progress indicator."""
        assert 'id="prog-indicator"' in accumulator_html or 'class="prog"' in accumulator_html

    def test_references_local_scripts(self, accumulator_html):
        """Tutorial must reference only theme.js and highlight.js."""
        assert 'src="assets/theme.js"' in accumulator_html
        assert 'src="assets/highlight.js"' in accumulator_html

    def test_each_row_has_required_subheadings(self, accumulator_html):
        """Each row must have Purpose/I/O/Why/Pitfalls subheadings."""
        assert accumulator_html.count('<h4>Purpose</h4>') >= 5, "Need 5 Purpose subheadings"
        assert accumulator_html.count('<h4>I/O</h4>') >= 5, "Need 5 I/O subheadings"
        assert accumulator_html.count('<h4>Why</h4>') >= 5, "Need 5 Why subheadings"
        assert accumulator_html.count('<h4>Pitfalls</h4>') >= 5, "Need 5 Pitfalls subheadings"

    def test_no_external_assets(self, accumulator_html):
        """Tutorial must have no external asset references (security)."""
        for pattern in EXTERNAL_PATTERNS:
            matches = re.findall(pattern, accumulator_html, re.IGNORECASE)
            assert not matches, f"Found external reference matching: {pattern}"

    def test_has_accumulator_content(self, accumulator_html):
        """Tutorial must have accumulator-specific content."""
        assert "NetFlowAccumulator" in accumulator_html
        assert "outflow" in accumulator_html
        assert "inflow" in accumulator_html
        assert "update" in accumulator_html
        assert "net_flow" in accumulator_html

    def test_has_option3_grounding_facts_line(self, accumulator_html):
        """Tutorial must have Option 3 compact facts line with dl."""
        assert 'class="gnd-facts"' in accumulator_html, "Missing .gnd-facts container"
        assert "<dl>" in accumulator_html, "Missing dl element for facts"
        assert "<dt>" in accumulator_html, "Missing dt elements"
        assert "<dd>" in accumulator_html, "Missing dd elements"

    def test_has_option3_expandable_details(self, accumulator_html):
        """Tutorial must have Option 3 expandable details/summary for rationale."""
        assert 'class="gnd-details"' in accumulator_html, "Missing .gnd-details"
        assert "<details" in accumulator_html, "Missing details element"
        assert "<summary>" in accumulator_html, "Missing summary element"
        assert 'class="gnd-content"' in accumulator_html, "Missing .gnd-content"

    def test_grounding_has_key_invariants(self, accumulator_html):
        """Grounding facts must include key invariants."""
        assert "O(N)" in accumulator_html
        assert "Diagonal" in accumulator_html
        assert "Preconditions" in accumulator_html

    def test_no_deterministic_output_assertions(self, accumulator_html):
        """Tutorial must not have deterministic output assertions."""
        assert "outflow[0] =" not in accumulator_html
        assert "expected outflow" not in accumulator_html.lower()

    def test_has_io_summary(self, accumulator_html):
        """Tutorial must have I/O Summary section."""
        assert 'class="io-summary"' in accumulator_html
        assert "I/O Summary" in accumulator_html

    def test_has_usage_disclaimer(self, accumulator_html):
        """Tutorial must have usage disclaimer about illustrative examples."""
        assert 'class="usage-disclaimer"' in accumulator_html
        assert "illustrative" in accumulator_html.lower()
        assert "do not treat" in accumulator_html.lower()

    def test_mentions_o_n_memory(self, accumulator_html):
        """Tutorial must mention O(N) memory benefit."""
        assert "O(N)" in accumulator_html

    def test_mentions_block_tiling(self, accumulator_html):
        """Tutorial must mention block tiling/iteration."""
        assert "block" in accumulator_html.lower()

    def test_has_preconditions_wording(self, accumulator_html):
        """Tutorial must label bounds as preconditions."""
        assert "Preconditions" in accumulator_html or "precondition" in accumulator_html.lower()
        assert "not enforced here" in accumulator_html.lower()

    def test_has_conditional_flow_conservation(self, accumulator_html):
        """Tutorial must make flow conservation conditional on correct tiling."""
        assert "if tiling covers" in accumulator_html.lower() or "if tiling is correct" in accumulator_html.lower()

    def test_normalize_mentions_min_max(self, accumulator_html):
        """Tutorial must clarify normalize() uses min-max scaling."""
        assert "min-max" in accumulator_html.lower()

    def test_normalize_mentions_hides_scale(self, accumulator_html):
        """Tutorial must note normalize() hides absolute scale."""
        assert "hides absolute scale" in accumulator_html.lower() or "hide" in accumulator_html.lower()

    def test_flow_conservation_mentions_exactly_once(self, accumulator_html):
        """Tutorial must mention tiling covers pairs exactly once."""
        assert "exactly once" in accumulator_html.lower()

    def test_flow_conservation_mentions_no_overlap(self, accumulator_html):
        """Tutorial must mention no overlap in tiling."""
        assert "no overlap" in accumulator_html.lower()

    def test_flow_conservation_mentions_no_gaps(self, accumulator_html):
        """Tutorial must mention no gaps in tiling."""
        assert "no gaps" in accumulator_html.lower()

    def test_normalize_mentions_outliers(self, accumulator_html):
        """Tutorial must mention normalize() sensitivity to outliers."""
        assert "outlier" in accumulator_html.lower()

    def test_normalize_mentions_convention(self, accumulator_html):
        """Tutorial must note 0.5 for all-equal is a convention."""
        assert "convention" in accumulator_html.lower()

    def test_flow_conservation_mentions_same_weights_for_all_blocks(self, accumulator_html):
        """Tutorial must mention same weights for all blocks."""
        assert "same weights" in accumulator_html.lower()
        assert "for all blocks" in accumulator_html.lower()

    def test_flow_conservation_mentions_floating_point_tolerance(self, accumulator_html):
        """Tutorial must mention floating-point tolerance instead of approximate symbol."""
        assert "floating-point" in accumulator_html.lower() or "tolerance" in accumulator_html.lower()
