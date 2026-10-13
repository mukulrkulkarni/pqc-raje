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
