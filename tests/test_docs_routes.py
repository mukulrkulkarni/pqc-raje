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
