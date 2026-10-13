"""Tests for preview/confirmation gate functionality."""

import json
import numpy as np
import pytest
import tempfile
from pathlib import Path

from app import create_app
from app.routes.preview import is_upload_confirmed, mark_upload_confirmed, clear_upload_confirmation
from app.services.security import register_upload, get_upload_path


@pytest.fixture
def app():
    """Create test application."""
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_matrix(tmp_path):
    """Create a sample matrix file."""
    matrix = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    path = tmp_path / "test_matrix.npy"
    np.save(path, matrix)
    return path


class TestConfirmationState:
    """Tests for confirmation state management."""

    def test_initial_state_not_confirmed(self, app):
        """New uploads should not be confirmed."""
        with app.test_request_context():
            assert not is_upload_confirmed("new-upload-123")

    def test_mark_confirmed(self, app):
        """Should be able to mark upload as confirmed."""
        with app.test_request_context():
            from flask import session
            session["confirmed_uploads"] = []
            mark_upload_confirmed("test-upload")
            assert is_upload_confirmed("test-upload")

    def test_clear_confirmation(self, app):
        """Should be able to clear confirmation."""
        with app.test_request_context():
            from flask import session
            session["confirmed_uploads"] = ["test-upload"]
            clear_upload_confirmation("test-upload")
            assert not is_upload_confirmed("test-upload")

    def test_session_scoped(self, app):
        """Confirmations should be session-scoped."""
        with app.test_request_context():
            from flask import session
            session["confirmed_uploads"] = []
            mark_upload_confirmed("upload-a")
            assert is_upload_confirmed("upload-a")
            assert not is_upload_confirmed("upload-b")


class TestPreviewRoutes:
    """Tests for preview routes."""

    def test_preview_not_found(self, client):
        """Preview for unknown upload should return 404."""
        response = client.get("/preview/nonexistent-id")
        assert response.status_code == 404

    def test_preview_shows_matrix(self, client, sample_matrix):
        """Preview should show matrix info."""
        register_upload("test-id", sample_matrix)
        response = client.get("/preview/test-id")
        assert response.status_code == 200
        assert b"3" in response.data  # 3 rows

    def test_confirm_sets_state(self, client, sample_matrix):
        """Confirm should set confirmation state."""
        register_upload("confirm-test", sample_matrix)
        with client.session_transaction() as sess:
            sess["confirmed_uploads"] = []

        response = client.post("/preview/confirm-test/confirm")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "confirmed"

    def test_cancel_clears_state(self, client, sample_matrix):
        """Cancel should clear confirmation state."""
        register_upload("cancel-test", sample_matrix)
        with client.session_transaction() as sess:
            sess["confirmed_uploads"] = ["cancel-test"]

        response = client.post("/preview/cancel-test/cancel")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "cancelled"

    def test_confirm_not_found(self, client):
        """Confirm for unknown upload should return 404."""
        response = client.post("/preview/nonexistent/confirm")
        assert response.status_code == 404


class TestComputeGate:
    """Tests for compute route confirmation gate."""

    def test_compute_requires_confirmation(self, client, sample_matrix):
        """Compute should require confirmation."""
        register_upload("unconfirmed", sample_matrix)

        response = client.post(
            "/compute/start",
            json={"upload_id": "unconfirmed", "criteria": [{"weight": 1, "q": 1, "p": 2, "v": 3}]},
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_compute_allowed_after_confirm(self, client, sample_matrix):
        """Compute should work after confirmation."""
        register_upload("confirmed", sample_matrix)
        with client.session_transaction() as sess:
            sess["confirmed_uploads"] = ["confirmed"]

        response = client.post(
            "/compute/start",
            json={
                "upload_id": "confirmed",
                "criteria": [
                    {"weight": 1, "q": 1, "p": 2, "v": 3},
                    {"weight": 1, "q": 1, "p": 2, "v": 3},
                ],
            },
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_compute_missing_upload_id(self, client):
        """Compute without upload_id should return 400."""
        response = client.post(
            "/compute/start",
            json={"criteria": []},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_compute_missing_criteria(self, client, sample_matrix):
        """Compute without criteria should return 400."""
        register_upload("no-criteria", sample_matrix)
        with client.session_transaction() as sess:
            sess["confirmed_uploads"] = ["no-criteria"]

        response = client.post(
            "/compute/start",
            json={"upload_id": "no-criteria"},
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_compute_invalid_criteria(self, client, sample_matrix):
        """Compute with invalid criteria should return 400."""
        register_upload("invalid-criteria", sample_matrix)
        with client.session_transaction() as sess:
            sess["confirmed_uploads"] = ["invalid-criteria"]

        response = client.post(
            "/compute/start",
            json={
                "upload_id": "invalid-criteria",
                "criteria": [{"weight": 0, "q": 1, "p": 2, "v": 3}],  # Invalid weight
            },
            content_type="application/json",
        )
        assert response.status_code == 400


class TestSecurityService:
    """Tests for security service functions."""

    def test_register_and_get_upload(self, sample_matrix):
        """Should be able to register and retrieve uploads."""
        register_upload("sec-test", sample_matrix)
        retrieved = get_upload_path("sec-test")
        assert retrieved == sample_matrix

    def test_get_unregistered_upload(self):
        """Unregistered upload should return None."""
        result = get_upload_path("never-registered")
        assert result is None
