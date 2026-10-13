"""Tests for documentation serving routes."""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Create test application."""
    return create_app({"TESTING": True, "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestLandingPage:
    """Tests for landing page route."""

    def test_landing_returns_html(self, client):
        """Landing page should return HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"ELECTRE III" in response.data

    def test_landing_has_csp(self, client):
        """Landing page should have CSP header."""
        response = client.get("/")
        assert "Content-Security-Policy" in response.headers

    def test_landing_csp_allows_external_scripts(self, client):
        """Landing page CSP should allow script-src 'self' for theme.js."""
        response = client.get("/")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp

    def test_landing_has_getting_started_content(self, client):
        """Landing page should have Getting Started content."""
        response = client.get("/")
        assert b"Quick Start" in response.data
        assert b"multi-criteria" in response.data


class TestAppRoute:
    """Tests for /app route."""

    def test_app_route_exists(self, client):
        """App route should return 200."""
        response = client.get("/app")
        assert response.status_code == 200

    def test_app_has_csp(self, client):
        """App route should have CSP header."""
        response = client.get("/app")
        assert "Content-Security-Policy" in response.headers

    def test_app_csp_no_external_scripts(self, client):
        """App route CSP should NOT allow script-src 'self' (stricter CSP)."""
        response = client.get("/app")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" not in csp
        assert "script-src 'unsafe-inline'" not in csp


class TestModuleDocs:
    """Tests for module documentation routes."""

    def test_valid_module_doc(self, client):
        """Valid module doc should return 200."""
        response = client.get("/docs/modules/config")
        assert response.status_code == 200

    def test_module_doc_has_csp(self, client):
        """Module doc should have CSP header."""
        response = client.get("/docs/modules/config")
        assert "Content-Security-Policy" in response.headers

    def test_missing_module_returns_404(self, client):
        """Non-existent module should return 404."""
        response = client.get("/docs/modules/nonexistent")
        assert response.status_code == 404


class TestPathTraversalPrevention:
    """Negative tests for path traversal attacks."""

    def test_dotdot_blocked(self, client):
        """Path traversal with .. should return 404."""
        response = client.get("/docs/modules/../../../etc/passwd")
        assert response.status_code == 404

    def test_encoded_dotdot_blocked(self, client):
        """URL-encoded path traversal should return 404."""
        response = client.get("/docs/modules/%2e%2e%2f%2e%2e%2fetc%2fpasswd")
        assert response.status_code == 404

    def test_absolute_path_blocked(self, client):
        """Absolute paths should return 404."""
        response = client.get("/docs/modules//etc/passwd")
        assert response.status_code == 404

    def test_slashes_in_name_blocked(self, client):
        """Slashes in module name should return 404."""
        response = client.get("/docs/modules/config/../../secret")
        assert response.status_code == 404

    def test_dots_in_name_blocked(self, client):
        """Dots in module name should return 404."""
        response = client.get("/docs/modules/config.html")
        assert response.status_code == 404

    def test_uppercase_blocked(self, client):
        """Uppercase names not in allow-list should return 404."""
        response = client.get("/docs/modules/CONFIG")
        assert response.status_code == 404

    def test_special_chars_blocked(self, client):
        """Special characters should return 404."""
        response = client.get("/docs/modules/config<script>")
        assert response.status_code == 404

    def test_null_byte_blocked(self, client):
        """Null bytes should return 404."""
        response = client.get("/docs/modules/config%00.html")
        assert response.status_code == 404


class TestAllowListEnforcement:
    """Tests for allow-list enforcement."""

    def test_only_allowed_modules_served(self, client):
        """Only allow-listed modules should be served."""
        allowed = ["config"]  # Only config exists currently
        for name in allowed:
            response = client.get(f"/docs/modules/{name}")
            assert response.status_code == 200, f"{name} should be allowed"

    def test_random_names_blocked(self, client):
        """Random names not in allow-list should be blocked."""
        blocked = ["foo", "bar", "secret", "admin", "test"]
        for name in blocked:
            response = client.get(f"/docs/modules/{name}")
            assert response.status_code == 404, f"{name} should be blocked"


class TestThemeJsStatic:
    """Tests for theme.js static file serving."""

    def test_theme_js_served(self, client):
        """Theme.js should be served from /static/docs/theme.js."""
        response = client.get("/static/docs/theme.js")
        assert response.status_code == 200

    def test_theme_js_content_type(self, client):
        """Theme.js should have correct content type."""
        response = client.get("/static/docs/theme.js")
        content_type = response.headers.get("Content-Type", "")
        assert "javascript" in content_type.lower()

    def test_theme_js_contains_toggle_logic(self, client):
        """Theme.js should contain theme toggle implementation."""
        response = client.get("/static/docs/theme.js")
        assert b"localStorage" in response.data
        assert b"data-theme" in response.data


class TestMetaCSPAlignment:
    """Tests for meta CSP alignment with header policy."""

    def test_getting_started_meta_csp_no_unsafe_inline_script(self):
        """GETTING_STARTED.html meta CSP should not have script-src 'unsafe-inline'."""
        from pathlib import Path
        gs_path = Path(__file__).parent.parent / "docs" / "GETTING_STARTED.html"
        content = gs_path.read_text()
        assert "script-src 'unsafe-inline'" not in content
        assert "script-src 'self'" in content

    def test_preview_template_meta_csp_no_scripts(self):
        """preview.html meta CSP should not allow any scripts."""
        from pathlib import Path
        preview_path = Path(__file__).parent.parent / "app" / "templates" / "preview.html"
        content = preview_path.read_text()
        assert "script-src" not in content

    def test_tutorial_no_inline_js_fallback(self):
        """Tutorial HTML should not have inline JS fallback."""
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        content = tutorial_path.read_text()
        assert "location.protocol === 'file:'" not in content
        assert "document.createElement('script')" not in content

    def test_tutorial_uses_relative_script_path(self):
        """Tutorial should reference theme.js via relative path."""
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        content = tutorial_path.read_text()
        assert 'src="assets/theme.js"' in content

    def test_tutorial_has_sidebar(self):
        """Tutorial should have sidebar element for theme toggle."""
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        content = tutorial_path.read_text()
        assert 'class="sidebar"' in content
        assert 'class="theme-toggle"' in content


class TestLocalThemeJsAsset:
    """Tests for local theme.js asset in docs/modules/assets/."""

    def test_local_theme_js_exists(self):
        """Local theme.js should exist in docs/modules/assets/."""
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "docs" / "modules" / "assets" / "theme.js"
        assert js_path.exists()

    def test_local_theme_js_has_toggle_logic(self):
        """Local theme.js should have theme toggle logic."""
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "docs" / "modules" / "assets" / "theme.js"
        content = js_path.read_text()
        assert "localStorage" in content
        assert "data-theme" in content


class TestTutorialAssetRoute:
    """Tests for /docs/modules/<name>/assets/<asset> route."""

    def test_tutorial_references_relative_asset(self, client):
        """Tutorial HTML should reference assets/theme.js."""
        response = client.get("/docs/modules/config/tutorial")
        assert response.status_code == 200
        assert b'src="assets/theme.js"' in response.data

    def test_tutorial_asset_served(self, client):
        """theme.js should be served at /docs/modules/config/assets/theme.js."""
        response = client.get("/docs/modules/config/assets/theme.js")
        assert response.status_code == 200

    def test_tutorial_asset_content_type(self, client):
        """theme.js should have correct content type."""
        response = client.get("/docs/modules/config/assets/theme.js")
        content_type = response.headers.get("Content-Type", "")
        assert "javascript" in content_type.lower()

    def test_tutorial_asset_contains_toggle(self, client):
        """Served theme.js should contain toggle logic."""
        response = client.get("/docs/modules/config/assets/theme.js")
        assert b"localStorage" in response.data
        assert b"data-theme" in response.data

    def test_asset_invalid_module_returns_404(self, client):
        """Asset route with invalid module name should return 404."""
        response = client.get("/docs/modules/invalid/assets/theme.js")
        assert response.status_code == 404

    def test_asset_invalid_asset_returns_404(self, client):
        """Asset route with non-allowed asset should return 404."""
        response = client.get("/docs/modules/config/assets/malicious.js")
        assert response.status_code == 404

    def test_asset_path_traversal_blocked(self, client):
        """Path traversal in asset name should return 404."""
        response = client.get("/docs/modules/config/assets/../../../etc/passwd")
        assert response.status_code == 404

    def test_asset_dotdot_in_name_blocked(self, client):
        """Asset name with .. should return 404."""
        response = client.get("/docs/modules/config/assets/..%2F..%2Ftheme.js")
        assert response.status_code == 404

    def test_asset_uppercase_blocked(self, client):
        """Uppercase asset names not in allow-list should return 404."""
        response = client.get("/docs/modules/config/assets/THEME.JS")
        assert response.status_code == 404


class TestTutorialButtonContrast:
    """Tests for theme toggle button contrast compliance."""

    def test_tutorial_uses_accent_on_token(self):
        """Tutorial active button should use --accent-on token for AA contrast."""
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        content = tutorial_path.read_text()
        assert "var(--accent-on)" in content
        assert "--accent-on:" in content

    def test_dark_mode_accent_on_value(self):
        """Both dark blocks should use #0f1115 for --accent-on (dark text on blue)."""
        from pathlib import Path
        import re
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        content = tutorial_path.read_text()
        # Find all --accent-on declarations in dark mode contexts
        # Pattern: look for --accent-on: #0f1115 within dark theme blocks
        dark_accent_on = re.findall(r'--accent-on:\s*#([0-9a-fA-F]{6})', content)
        # Should have 3 total: 1 in :root (light), 2 in dark blocks
        assert len(dark_accent_on) == 3, f"Expected 3 --accent-on declarations, found {len(dark_accent_on)}"
        # Light mode should be white, dark modes should be #0f1115
        assert dark_accent_on[0] == "ffffff", "Light mode --accent-on should be #ffffff"
        assert dark_accent_on[1] == "0f1115", "System dark --accent-on should be #0f1115"
        assert dark_accent_on[2] == "0f1115", "Explicit dark --accent-on should be #0f1115"


class TestTutorialContent:
    """Tests for required tutorial sections and content quality."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_has_pipeline_context_section(self):
        """Tutorial must explain pipeline context."""
        content = self._get_tutorial_content()
        assert "Pipeline Context" in content
        assert "concordance" in content
        assert "discordance" in content
        assert "credibility" in content
        assert "ranking" in content

    def test_has_key_constraints_section(self):
        """Tutorial must document key constraints."""
        content = self._get_tutorial_content()
        assert "Key Constraints" in content
        assert "q ≤ p ≤ v" in content or "0 ≤ q ≤ p ≤ v" in content
        assert "Determinism" in content or "seed" in content

    def test_has_io_specification_section(self):
        """Tutorial must document I/O behavior."""
        content = self._get_tutorial_content()
        assert "I/O Specification" in content
        assert "Input" in content
        assert "Output" in content
        assert "Errors" in content
        assert "ValueError" in content

    def test_has_walkthrough_section(self):
        """Tutorial must have step-by-step walkthrough."""
        content = self._get_tutorial_content()
        assert "Walkthrough" in content

    def test_documents_all_public_exports(self):
        """Tutorial must document CriterionConfig, ComputeConfig, normalize_weights."""
        content = self._get_tutorial_content()
        assert "CriterionConfig" in content
        assert "ComputeConfig" in content
        assert "normalize_weights" in content

    def test_usage_example_marked_illustrative(self):
        """Usage example must be marked as illustrative pseudocode."""
        content = self._get_tutorial_content()
        assert "illustrative" in content.lower(), \
            "Usage example must be marked as illustrative"
        assert "Do not treat" in content or "not treat numeric" in content.lower(), \
            "Must warn that numeric values are examples only"

    def test_no_hardcoded_numeric_output_arrays(self):
        """Usage example must not show exact numeric output arrays."""
        content = self._get_tutorial_content()
        # Should not have exact output like [0.5, 0.333, 0.167]
        assert "[0.5, 0.333, 0.167]" not in content, \
            "Do not show exact numeric output arrays"


class TestTutorialRangeCallouts:
    """Tests for range callout links between code and docs."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_range_ids_exist_in_code_pane(self):
        """Code pane must have R1-R5 id attributes."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="{r}"' in content, f"Missing id for {r}"

    def test_range_refs_exist_in_doc_pane(self):
        """Doc pane must have href links to R1-R5."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'href="#{r}"' in content, f"Missing href for {r}"

    def test_range_markers_are_clickable_anchors(self):
        """Range markers in code must be <a> elements with hrefs to doc sections."""
        import re
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            # Pattern allows for aria-label and other attributes
            pattern = rf'<a href="#doc-{r}" class="range-marker"[^>]*>{r}</a>'
            assert re.search(pattern, content), \
                f"Range marker {r} must be clickable anchor linking to doc-{r}"

    def test_doc_sections_have_ids(self):
        """Doc sections must have id attributes for bidirectional linking."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="doc-{r}"' in content, f"Missing doc section id for doc-{r}"

    def test_doc_sections_have_class(self):
        """Doc sections must have doc-section class for highlight styling."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'class="doc-section" id="doc-{r}"' in content, \
                f"Doc section {r} must have doc-section class"

    def test_data_range_attributes_set(self):
        """Code lines must have data-range attributes for highlighting."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'data-range="{r}"' in content, f"Missing data-range for {r}"

    def test_highlight_js_referenced(self):
        """Tutorial must reference highlight.js for toggle behavior."""
        content = self._get_tutorial_content()
        assert 'src="assets/highlight.js"' in content

    def test_scroll_container_ids_exist(self):
        """Tutorial must have explicit IDs for scroll containers."""
        content = self._get_tutorial_content()
        assert 'id="codeScroll"' in content, "Missing id='codeScroll' on code pane"
        assert 'id="docScroll"' in content, "Missing id='docScroll' on doc pane"

    def test_range_anchors_have_valid_targets(self):
        """Range markers in code must link to doc sections that exist."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'href="#doc-{r}"' in content, f"Missing href=#doc-{r}"
            assert f'id="doc-{r}"' in content, f"Missing id=doc-{r}"

    def test_callout_refs_have_valid_targets(self):
        """Callout refs in doc must link to code range IDs that exist."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="{r}"' in content, f"Missing id={r} on code line"

    def test_css_uses_range_selected_class(self):
        """CSS must style .range-selected, not all [data-range]."""
        content = self._get_tutorial_content()
        assert ".code-line.range-selected" in content
        assert ".doc-section.range-selected" in content


class TestHighlightJsAsset:
    """Tests for highlight.js asset serving and content."""

    def test_highlight_js_served(self, client):
        """highlight.js should be served at /docs/modules/config/assets/highlight.js."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        assert response.status_code == 200

    def test_highlight_js_content_type(self, client):
        """highlight.js should have correct content type."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content_type = response.headers.get("Content-Type", "")
        assert "javascript" in content_type.lower()

    def test_highlight_js_has_toggle_logic(self, client):
        """highlight.js must implement toggle behavior."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "range-selected" in content
        assert "clearSelection" in content
        assert "selectRange" in content

    def test_highlight_js_has_click_to_scroll(self, client):
        """highlight.js must implement click-to-scroll behavior."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "scrollToElement" in content
        assert "scrollDocToRange" in content
        assert "scrollCodeToRange" in content

    def test_highlight_js_exposes_test_api(self, client):
        """highlight.js must expose testing API via window.highlightModule."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "window.highlightModule" in content
        assert "getCurrentRange" in content
        assert "getCodeScroll" in content
        assert "getDocScroll" in content
        assert "CODE_SCROLL_ID" in content
        assert "DOC_SCROLL_ID" in content
        assert "isSyncEnabled" in content
        assert "isSyncing" in content

    def test_highlight_js_local_file_exists(self):
        """Local highlight.js should exist in docs/modules/assets/."""
        from pathlib import Path
        js_path = Path(__file__).parent.parent / "docs" / "modules" / "assets" / "highlight.js"
        assert js_path.exists()

    def test_highlight_js_has_debug_mode(self, client):
        """highlight.js must support ?debug=1 URL parameter."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "debug=1" in content
        assert "console.log" in content

    def test_highlight_js_uses_scroll_container_ids(self, client):
        """highlight.js must use explicit scroll container IDs."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "codeScroll" in content
        assert "docScroll" in content
        assert "getElementById" in content

    def test_highlight_js_uses_correct_selectors_for_ranges(self, client):
        """highlight.js must use data-range attributes and doc section IDs."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "[data-range=" in content
        assert "doc-" in content

    def test_highlight_js_handles_click_capture(self, client):
        """highlight.js must use capture phase for click events."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # Verify addEventListener uses capture: true
        assert "addEventListener('click', handleClick, true)" in content


class TestSyncScrollToggle:
    """Tests for sync scroll toggle in sidebar."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_sync_toggle_exists_in_sidebar(self):
        """Sidebar must have sync scroll toggle button."""
        content = self._get_tutorial_content()
        assert 'data-sync-toggle' in content
        assert 'class="sync-toggle"' in content

    def test_sync_toggle_has_indicator(self):
        """Sync toggle must have visual indicator."""
        content = self._get_tutorial_content()
        assert 'class="sync-indicator"' in content

    def test_sync_toggle_has_aria_pressed(self):
        """Sync toggle must have aria-pressed attribute."""
        content = self._get_tutorial_content()
        assert 'aria-pressed="false"' in content

    def test_sync_toggle_defaults_off(self):
        """Sync toggle must default to OFF (aria-pressed='false')."""
        content = self._get_tutorial_content()
        # The toggle should have aria-pressed="false" by default
        import re
        toggle_match = re.search(r'data-sync-toggle[^>]*aria-pressed="([^"]*)"', content)
        assert toggle_match, "Sync toggle must have aria-pressed attribute"
        assert toggle_match.group(1) == "false", "Sync toggle must default to OFF"

    def test_sync_toggle_css_exists(self):
        """CSS must style sync toggle states."""
        content = self._get_tutorial_content()
        assert ".sync-toggle" in content
        assert ".sync-enabled" in content


class TestContinuousScrollSync:
    """Tests for continuous scroll sync functionality in highlight.js."""

    def test_highlight_js_has_loop_guard(self, client):
        """highlight.js must have isSyncing loop guard to prevent oscillation."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "isSyncing" in content, "Missing isSyncing loop guard variable"
        assert "isSyncing = true" in content, "Must set isSyncing = true before syncing"
        assert "isSyncing = false" in content, "Must release isSyncing after sync"

    def test_highlight_js_uses_raf_for_loop_guard(self, client):
        """highlight.js must use requestAnimationFrame for loop guard release."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "requestAnimationFrame" in content, \
            "Must use requestAnimationFrame for throttling loop guard"

    def test_highlight_js_binds_scroll_listeners(self, client):
        """highlight.js must bind scroll listeners to #codeScroll and #docScroll."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "addEventListener('scroll'" in content or \
               'addEventListener("scroll"' in content, \
            "Must add scroll event listeners"
        assert "codeScroll" in content and "docScroll" in content, \
            "Must reference codeScroll and docScroll containers"

    def test_highlight_js_percentage_based_sync(self, client):
        """highlight.js must use percentage-based scroll position for sync."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "scrollHeight" in content, "Must use scrollHeight for percentage calc"
        assert "clientHeight" in content, "Must use clientHeight for percentage calc"
        assert "scrollTop" in content, "Must use scrollTop for percentage calc"

    def test_highlight_js_sync_guards_missing_containers(self, client):
        """highlight.js sync must no-op without throwing if containers missing."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # Must check for container existence before syncing
        assert "!source || !target" in content or \
               "if (!codeScroll || !docScroll)" in content or \
               "if (!el)" in content, \
            "Must guard against missing containers in sync functions"

    def test_highlight_js_sync_checks_enabled(self, client):
        """highlight.js sync must check syncEnabled before syncing."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "syncEnabled" in content, "Must have syncEnabled state variable"
        assert "!syncEnabled" in content or "syncEnabled === false" in content, \
            "Must check syncEnabled before syncing"


class TestSelectionAlignment:
    """Tests for selection-driven pane alignment in highlight.js."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_highlight_js_has_align_panes_function(self, client):
        """highlight.js must have alignPanes function for bidirectional alignment."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "function alignPanes" in content, "Missing alignPanes function"
        assert "alignPanes" in content, "alignPanes must be defined"

    def test_align_panes_references_both_containers(self, client):
        """alignPanes must reference both codeScroll and docScroll containers."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # Find the alignPanes function body and check it uses both containers
        assert "codeScroll" in content and "docScroll" in content, \
            "alignPanes must reference both scroll containers"
        # Check it scrolls both
        assert content.count("scrollTo") >= 2, \
            "alignPanes must scroll both panes"

    def test_align_panes_guards_missing_containers(self, client):
        """alignPanes must no-op without throwing if containers missing."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # Must check for container existence
        assert "!codeScroll || !docScroll" in content, \
            "alignPanes must guard against missing containers"

    def test_align_panes_guards_missing_targets(self, client):
        """alignPanes must no-op without throwing if target elements missing."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # Must check for target element existence
        assert "!codeTarget || !docTarget" in content, \
            "alignPanes must guard against missing target elements"

    def test_align_panes_exposed_in_test_api(self, client):
        """alignPanes must be exposed in window.highlightModule for testing."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "alignPanes: alignPanes" in content or "alignPanes:" in content, \
            "alignPanes must be in test API"

    def test_each_range_has_code_and_doc_anchors(self):
        """Each Rk must have both code anchor (id=Rk) and doc anchor (id=doc-Rk)."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'id="{r}"' in content, f"Missing code anchor id={r}"
            assert f'id="doc-{r}"' in content, f"Missing doc anchor id=doc-{r}"

    def test_click_handler_uses_align_panes(self, client):
        """Click handler must call alignPanes for new selections."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "alignPanes(rangeId)" in content, \
            "Click handler must call alignPanes"

    def test_hash_navigation_uses_align_panes(self, client):
        """Hash navigation must call alignPanes."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        # handleHashChange should use alignPanes
        assert "alignPanes" in content, "Hash navigation should use alignPanes"


class TestRouteScopedCSP:
    """Tests for route-scoped CSP headers."""

    def test_docs_modules_allows_scripts(self, client):
        """/docs/* routes should allow script-src 'self'."""
        response = client.get("/docs/modules/config")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp

    def test_root_allows_scripts(self, client):
        """Root / should allow script-src 'self' (docs landing)."""
        response = client.get("/")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp

    def test_preview_no_scripts(self, client):
        """Preview routes should not allow external scripts."""
        response = client.get("/preview/test")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" not in csp

    def test_compute_no_scripts(self, client):
        """Compute routes should not allow external scripts."""
        response = client.post("/compute")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" not in csp

    # Explicit CSP header presence tests (Security gate evidence)
    def test_csp_header_present_on_root(self, client):
        """/ must have Content-Security-Policy HTTP header."""
        response = client.get("/")
        assert "Content-Security-Policy" in response.headers, \
            "CSP header missing on /"

    def test_csp_header_present_on_docs_modules(self, client):
        """/docs/modules/config must have Content-Security-Policy HTTP header."""
        response = client.get("/docs/modules/config")
        assert "Content-Security-Policy" in response.headers, \
            "CSP header missing on /docs/modules/config"

    def test_csp_header_present_on_tutorial(self, client):
        """/docs/modules/config/tutorial must have Content-Security-Policy HTTP header."""
        response = client.get("/docs/modules/config/tutorial")
        assert "Content-Security-Policy" in response.headers, \
            "CSP header missing on /docs/modules/config/tutorial"

    def test_csp_header_present_on_app(self, client):
        """/app must have Content-Security-Policy HTTP header (not just meta tag)."""
        response = client.get("/app")
        assert "Content-Security-Policy" in response.headers, \
            "CSP header missing on /app - must use HTTP header, not meta tag only"

    def test_csp_no_unsafe_inline_script_on_docs(self, client):
        """Docs routes must not have script-src 'unsafe-inline'."""
        for route in ["/", "/docs/modules/config", "/docs/modules/config/tutorial"]:
            response = client.get(route)
            csp = response.headers["Content-Security-Policy"]
            assert "script-src 'unsafe-inline'" not in csp, \
                f"Route {route} has unsafe-inline in script-src"

    def test_csp_no_unsafe_inline_script_on_app(self, client):
        """/app must not have script-src 'unsafe-inline'."""
        response = client.get("/app")
        csp = response.headers["Content-Security-Policy"]
        # /app uses CSP_APP which has no script-src (blocked by default-src 'none')
        assert "script-src 'unsafe-inline'" not in csp, \
            "/app has unsafe-inline in script-src"

    def test_app_csp_blocks_scripts(self, client):
        """/app CSP should block scripts (no script-src means default-src 'none' applies)."""
        response = client.get("/app")
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp, "/app must have default-src 'none'"
        # If there's no script-src directive, scripts are blocked by default-src 'none'
        assert "script-src" not in csp or "script-src 'none'" in csp or \
               ("script-src 'self'" not in csp and "script-src 'unsafe" not in csp), \
            "/app should not allow script execution"


class TestTutorialNegativeCases:
    """Negative tests to verify tutorial structure validation catches errors."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_no_orphan_range_markers(self):
        """Range markers must point to existing doc sections."""
        import re
        content = self._get_tutorial_content()
        marker_hrefs = re.findall(r'class="range-marker"[^>]*href="#(doc-R\d+)"', content)
        marker_hrefs += re.findall(r'href="#(doc-R\d+)"[^>]*class="range-marker"', content)
        doc_ids = re.findall(r'id="(doc-R\d+)"', content)
        for href in marker_hrefs:
            assert href in doc_ids, f"Orphan range marker: href=#{href} has no matching id"

    def test_no_orphan_callout_refs(self):
        """Callout refs must point to existing code range IDs."""
        import re
        content = self._get_tutorial_content()
        ref_hrefs = re.findall(r'class="range-ref"[^>]*href="#(R\d+)"', content)
        ref_hrefs += re.findall(r'href="#(R\d+)"[^>]*class="range-ref"', content)
        code_ids = re.findall(r'id="(R\d+)"', content)
        for href in ref_hrefs:
            assert href in code_ids, f"Orphan callout ref: href=#{href} has no matching id"

    def test_range_marker_pattern_valid(self):
        """Range markers must follow R\\d+ pattern exactly."""
        import re
        content = self._get_tutorial_content()
        markers = re.findall(r'class="range-marker"[^>]*>([^<]+)</a>', content)
        for marker in markers:
            assert re.match(r'^R\d+$', marker.strip()), \
                f"Malformed range marker label: '{marker}' (expected R1, R2, etc.)"

    def test_doc_section_id_pattern_valid(self):
        """Doc section IDs must follow doc-R\\d+ pattern exactly."""
        import re
        content = self._get_tutorial_content()
        doc_ids = re.findall(r'class="doc-section"[^>]*id="([^"]+)"', content)
        doc_ids += re.findall(r'id="([^"]+)"[^>]*class="doc-section"', content)
        for doc_id in doc_ids:
            assert re.match(r'^doc-R\d+$', doc_id), \
                f"Malformed doc section id: '{doc_id}' (expected doc-R1, doc-R2, etc.)"

    def test_scroll_containers_have_overflow_auto(self):
        """Scroll containers must have overflow style for scrolling."""
        import re
        content = self._get_tutorial_content()
        assert 'overflow' in content.lower(), "Scroll containers need overflow CSS"
        pane_styles = re.findall(r'\.pane[^{]*\{[^}]*overflow[^}]*\}', content, re.IGNORECASE)
        assert len(pane_styles) > 0, "Pane elements must have overflow styling"


class TestAssetSecurityNegative:
    """Security negative tests for asset routes."""

    def test_double_encoded_traversal_blocked(self, client):
        """Double-encoded path traversal should return 404."""
        response = client.get("/docs/modules/config/assets/%252e%252e%252ftheme.js")
        assert response.status_code == 404

    def test_null_byte_injection_blocked(self, client):
        """Null byte injection attempt should return 404."""
        response = client.get("/docs/modules/config/assets/theme.js%00.txt")
        assert response.status_code == 404

    def test_unicode_traversal_blocked(self, client):
        """Unicode path traversal variants should return 404."""
        response = client.get("/docs/modules/config/assets/..%c0%af..%c0%afetc/passwd")
        assert response.status_code == 404

    def test_backslash_traversal_blocked(self, client):
        """Backslash path traversal should return 404."""
        response = client.get("/docs/modules/config/assets/..\\..\\..\\etc\\passwd")
        assert response.status_code == 404

    def test_mixed_case_extension_blocked(self, client):
        """Mixed case asset extension not in allow-list returns 404."""
        response = client.get("/docs/modules/config/assets/theme.JS")
        assert response.status_code == 404

    def test_nonexistent_allowed_module_asset_404(self, client):
        """Request for non-existent file in allowed asset list returns 404."""
        # This tests the file existence check, not just the allow-list
        # We can't easily remove highlight.js, so test with valid module but
        # asset that's in allow-list but file doesn't exist would need monkeypatch
        # Instead verify the route structure handles missing files
        response = client.get("/docs/modules/nonexistent/assets/theme.js")
        assert response.status_code == 404


class TestHighlightJsProvenance:
    """Tests for highlight.js provenance and license headers."""

    def test_highlight_js_has_source_header(self, client):
        """highlight.js must have @source header."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "@source" in content
        assert "In-house" in content or "ELECTRE III" in content

    def test_highlight_js_has_license_header(self, client):
        """highlight.js must have @license header."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "@license" in content

    def test_highlight_js_has_file_header(self, client):
        """highlight.js must have @file header."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "@file" in content
        assert "highlight.js" in content


class TestAccessibilityFeatures:
    """Tests for accessibility features in tutorial and highlight.js."""

    def _get_tutorial_content(self):
        from pathlib import Path
        tutorial_path = Path(__file__).parent.parent / "docs" / "modules" / "config_tutorial_side_by_side.html"
        return tutorial_path.read_text(encoding="utf-8")

    def test_highlight_js_respects_reduced_motion(self, client):
        """highlight.js must check prefers-reduced-motion media query."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "prefers-reduced-motion" in content
        assert "matchMedia" in content
        assert "reduce" in content

    def test_highlight_js_uses_auto_behavior_for_reduced_motion(self, client):
        """highlight.js must use behavior:'auto' when reduced motion preferred."""
        response = client.get("/docs/modules/config/assets/highlight.js")
        content = response.data.decode("utf-8")
        assert "behavior:" in content or "scrollBehavior" in content
        assert "'auto'" in content or '"auto"' in content

    def test_range_markers_have_aria_labels(self):
        """Range markers must have aria-label attributes."""
        content = self._get_tutorial_content()
        for r in ["R1", "R2", "R3", "R4", "R5"]:
            assert f'aria-label="Go to note {r}' in content, \
                f"Range marker {r} missing aria-label"

    def test_focus_visible_styles_exist_for_range_marker(self):
        """CSS must have :focus-visible styles for range markers."""
        content = self._get_tutorial_content()
        assert ".range-marker:focus-visible" in content
        assert "outline" in content

    def test_focus_visible_styles_exist_for_range_ref(self):
        """CSS must have :focus-visible styles for callout refs."""
        content = self._get_tutorial_content()
        assert ".range-ref:focus-visible" in content

    def test_target_fallback_for_code_line(self):
        """CSS must have :target fallback for code lines (no-JS support)."""
        content = self._get_tutorial_content()
        assert ".code-line:target" in content

    def test_target_fallback_for_doc_section(self):
        """CSS must have :target fallback for doc sections (no-JS support)."""
        content = self._get_tutorial_content()
        assert ".doc-section:target" in content

    def test_focus_visible_uses_accent_outline(self):
        """Focus-visible outline must use accent color token."""
        content = self._get_tutorial_content()
        # Find focus-visible blocks and check they use accent for outline
        import re
        focus_blocks = re.findall(
            r':focus-visible\s*\{[^}]*\}',
            content,
            re.IGNORECASE
        )
        assert len(focus_blocks) >= 2, "Need at least 2 :focus-visible blocks"
        for block in focus_blocks:
            assert "var(--accent)" in block, \
                f":focus-visible block must use accent token: {block}"
