"""Focused tests for the server-rendered /app workflow."""
import re

import pytest

from app import create_app

CRITERIA = '[{"name":"Quality","weight":0.5,"q":0,"p":0.2,"v":0.5,"maximize":true},{"name":"Cost","weight":0.5,"q":0,"p":0.2,"v":0.5,"maximize":false}]'
HEADERED = "Asset ID,Quality,Cost\nA,0.9,0.2\nB,0.5,0.8\nC,0.7,0.4\n"


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "workflow-test"})
    return app.test_client()


def _criteria(client):
    return client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": CRITERIA})


def _preview(client, csv=HEADERED, **extra):
    data = {"matrix_csv": csv, "header_mode": "headered", "missing_replacement": "0"}
    data.update(extra)
    return client.post("/app/preview", data=data)


def test_get_app_has_accessible_criteria_modes_and_no_scripts(client):
    response = client.get("/app/")
    assert response.status_code == 200
    assert b'name="criteria_mode"' in response.data
    assert b"Paste JSON" in response.data and b"Fill form" in response.data
    assert b"<script" not in response.data.lower()
    assert b"onload=" not in response.data.lower()
    assert "script-src" not in response.headers["Content-Security-Policy"]
    assert "script-src" not in (open("app/templates/config.html", encoding="utf-8").read())


def test_complete_workflow_displays_top_scores_and_mapping(client):
    assert _criteria(client).status_code == 200
    preview = _preview(client)
    assert preview.status_code == 200
    assert b"Validation report" in preview.data
    assert b"Header mapping" in preview.data
    assert b"Quality" in preview.data
    result = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert result.status_code == 200
    assert b"Raw net flow" in result.data
    assert b">A<" in result.data
    assert b"<script" not in result.data.lower()


def test_compute_requires_preview_and_confirmation(client):
    _criteria(client)
    response = client.post("/app/compute", data={"confirm_compute": "yes"})
    assert response.status_code == 400
    _preview(client)
    response = client.post("/app/compute", data={})
    assert response.status_code == 400


def test_preview_reports_header_and_missing_value_errors(client):
    _criteria(client)
    wrong_header = _preview(client, "Asset ID,Cost,Quality\nA,0.9,0.2\nB,0.5,0.8\n")
    assert wrong_header.status_code == 400
    assert b"headers must match criteria names in order" in wrong_header.data
    missing = _preview(client, "Asset ID,Quality,Cost\nA,,0.2\nB,0.5,0.8\n")
    assert missing.status_code == 400
    assert b"missing-value approval" in missing.data


def test_missing_value_approval_replaces_with_default_zero(client):
    _criteria(client)
    response = _preview(client, "Asset ID,Quality,Cost\nA,,0.2\nB,0.5,0.8\n", approve_missing="yes")
    assert response.status_code == 200
    assert b">0.0<" in response.data


def test_rejects_out_of_range_scores_and_invalid_criteria(client):
    invalid = client.post("/app/confirm-inputs", data={"criteria_mode": "json", "criteria_json": "[]"})
    assert invalid.status_code == 400
    assert b"1 through 8" in invalid.data
    _criteria(client)
    response = _preview(client, "Asset ID,Quality,Cost\nA,1.1,0.2\nB,0.5,0.8\n")
    assert response.status_code == 400
    assert b"normalized to [0, 1]" in response.data


def test_download_serves_exact_cached_bytes_with_safe_headers(client):
    assert _criteria(client).status_code == 200
    assert _preview(client).status_code == 200
    result = client.post("/app/compute", data={"confirm_compute": "yes"})
    download_path = re.search(rb'href="(/app/download/[^"]+)"', result.data).group(1).decode()
    download = client.get(download_path)
    assert download.status_code == 200
    assert download.data.endswith(b"\n")
    assert download.headers["Cache-Control"] == "no-store"
    assert download.headers["X-Content-Type-Options"] == "nosniff"
    assert download.headers["Content-Disposition"] == 'attachment; filename="ranking-result.json"'
    assert download.headers["Content-Length"] == str(len(download.data))
    assert "script-src" not in download.headers["Content-Security-Policy"]


def test_download_rejects_unknown_token_and_preserves_compatibility_routes(client):
    assert client.get("/app/download/not-a-token").status_code == 404
    assert client.get("/").status_code == 200
    assert client.get("/docs/modules/config").status_code == 200
    assert client.post("/compute/start", json={}).status_code == 400
