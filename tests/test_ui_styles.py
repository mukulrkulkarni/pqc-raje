"""Tests for UI styles and accessibility."""

import pytest
from pathlib import Path

STATIC_DIR = Path(__file__).parent.parent / "app" / "static"
TEMPLATES_DIR = Path(__file__).parent.parent / "app" / "templates"


class TestStyleCSS:
    """Tests for style.css."""

    @pytest.fixture
    def style_css(self) -> str:
        """Load style.css content."""
        path = STATIC_DIR / "style.css"
        if not path.exists():
            pytest.skip("style.css not found")
        return path.read_text(encoding="utf-8")

    def test_has_design_tokens(self, style_css):
        """Should define CSS custom properties."""
        assert "--color-" in style_css
        assert "--space-" in style_css
        assert "--font-" in style_css

    def test_uses_arial_font(self, style_css):
        """Should use Arial font family."""
        assert "Arial" in style_css

    def test_has_responsive_breakpoint(self, style_css):
        """Should have responsive media query."""
        assert "@media" in style_css
        assert "768px" in style_css

    def test_has_visually_hidden(self, style_css):
        """Should have visually-hidden class for accessibility."""
        assert ".visually-hidden" in style_css

    def test_has_warning_box(self, style_css):
        """Should have warning box styles."""
        assert ".warning-box" in style_css or "warning" in style_css.lower()

    def test_has_info_grid(self, style_css):
        """Should have info grid layout."""
        assert ".info-grid" in style_css

    def test_has_button_styles(self, style_css):
        """Should have button styles."""
        assert ".btn" in style_css
        assert ".btn-primary" in style_css

    def test_has_table_styles(self, style_css):
        """Should have table styles."""
        assert "table" in style_css
        assert "th" in style_css
        assert "td" in style_css

    def test_has_data_label_responsive(self, style_css):
        """Should use data-label for responsive tables."""
        assert "data-label" in style_css


class TestPreviewTemplate:
    """Tests for preview.html template."""

    @pytest.fixture
    def preview_html(self) -> str:
        """Load preview.html content."""
        path = TEMPLATES_DIR / "preview.html"
        if not path.exists():
            pytest.skip("preview.html not found")
        return path.read_text(encoding="utf-8")

    def test_has_doctype(self, preview_html):
        """Should have DOCTYPE declaration."""
        assert "<!DOCTYPE html>" in preview_html

    def test_has_viewport(self, preview_html):
        """Should have viewport meta tag."""
        assert "viewport" in preview_html

    def test_has_csp(self, preview_html):
        """Should have Content-Security-Policy."""
        assert "Content-Security-Policy" in preview_html

    def test_has_aria_labels(self, preview_html):
        """Should have ARIA labels for accessibility."""
        assert "aria-label" in preview_html

    def test_has_scope_attributes(self, preview_html):
        """Should have scope attributes on table headers."""
        assert 'scope="col"' in preview_html or 'scope="row"' in preview_html

    def test_has_data_labels(self, preview_html):
        """Should have data-label attributes for responsive."""
        assert "data-label" in preview_html

    def test_has_warning_role(self, preview_html):
        """Warning box should have role=alert."""
        assert 'role="alert"' in preview_html


class TestConfigTemplate:
    """Tests for config.html template."""

    @pytest.fixture
    def config_html(self) -> str:
        """Load config.html content."""
        path = TEMPLATES_DIR / "config.html"
        if not path.exists():
            pytest.skip("config.html not found")
        return path.read_text(encoding="utf-8")

    def test_has_doctype(self, config_html):
        """Should have DOCTYPE declaration."""
        assert "<!DOCTYPE html>" in config_html

    def test_has_csp(self, config_html):
        """Should have Content-Security-Policy."""
        assert "Content-Security-Policy" in config_html

    def test_has_form(self, config_html):
        """Should have criteria form."""
        assert "<form" in config_html

    def test_has_input_labels(self, config_html):
        """Should have aria-label on inputs."""
        assert "aria-label" in config_html

    def test_has_required_inputs(self, config_html):
        """Should have required attribute on inputs."""
        assert "required" in config_html

    def test_has_threshold_inputs(self, config_html):
        """Should have inputs for q, p, v thresholds."""
        assert 'name="q_' in config_html or "q_" in config_html
        assert 'name="p_' in config_html or "p_" in config_html
        assert 'name="v_' in config_html or "v_" in config_html
