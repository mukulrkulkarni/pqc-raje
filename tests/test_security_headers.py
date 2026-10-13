"""Tests for Flask security response headers."""
import pytest
import numpy as np
from pathlib import Path
from app import create_app
from app.services.security import register_upload


@pytest.fixture
def app():
    """Create test application."""
    return create_app({"TESTING": True, "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_upload(tmp_path):
    """Create sample matrix and register it."""
    matrix = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    path = tmp_path / "test.npy"
    np.save(path, matrix)
    register_upload("test-headers", path)
    return "test-headers"


class TestSecurityHeaders:
    """Tests for security headers on responses."""

    def test_csp_header_on_preview(self, client, sample_upload):
        """Preview route should have CSP header."""
        response = client.get(f"/preview/{sample_upload}")
        assert response.status_code == 200
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'none'" in response.headers["Content-Security-Policy"]

    def test_x_content_type_options(self, client, sample_upload):
        """Response should have X-Content-Type-Options: nosniff."""
        response = client.get(f"/preview/{sample_upload}")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    def test_referrer_policy(self, client, sample_upload):
        """Response should have Referrer-Policy: no-referrer."""
        response = client.get(f"/preview/{sample_upload}")
        assert response.headers.get("Referrer-Policy") == "no-referrer"

    def test_coop_header(self, client, sample_upload):
        """Response should have Cross-Origin-Opener-Policy."""
        response = client.get(f"/preview/{sample_upload}")
        assert response.headers.get("Cross-Origin-Opener-Policy") == "same-origin"

    def test_corp_header(self, client, sample_upload):
        """Response should have Cross-Origin-Resource-Policy."""
        response = client.get(f"/preview/{sample_upload}")
        assert response.headers.get("Cross-Origin-Resource-Policy") == "same-origin"

    def test_csp_on_json_response(self, client):
        """JSON responses should also have security headers."""
        response = client.get("/preview/nonexistent")
        assert response.status_code == 404
        assert "Content-Security-Policy" in response.headers

    def test_csp_on_post_response(self, client, sample_upload):
        """POST responses should have security headers."""
        response = client.post(f"/preview/{sample_upload}/confirm")
        assert "Content-Security-Policy" in response.headers
