"""H2 architecture-hotfix regression tests."""
import os
import subprocess
from pathlib import Path

from app import create_app
from scripts.preflight.ownership import check_generated_docs

ROOT = Path(__file__).parent.parent


def test_preflight_checks_flask_csp_headers_not_template_text():
    app = create_app({"TESTING": True, "SECRET_KEY": "h2"})
    for route in ("/", "/app/", "/docs/modules/config", "/preview/missing"):
        header = app.test_client().get(route).headers["Content-Security-Policy"]
        assert "default-src 'none'" in header


def test_generated_docs_positive_and_manifest_ownership():
    assert "source" in (ROOT / "docs" / "GENERATED_DOCUMENTATION.md").read_text().lower()
    assert check_generated_docs().passed


def test_generated_docs_reject_stale_output():
    source = ROOT / "docs" / "modules" / "config_tutorial_side_by_side.html"
    target = ROOT / "website" / "modules" / "config" / "tutorial" / "index.html"
    original = target.stat().st_mtime
    older = source.stat().st_mtime - 2
    os.utime(target, (older, older))
    try:
        result = check_generated_docs()
        assert not result.passed
        assert any("stale" in message for message in result.messages)
    finally:
        os.utime(target, (original, original))


def test_legacy_routes_remain_documented_and_compatible():
    text = (ROOT / "docs" / "runbook" / "debugging.md").read_text(encoding="utf-8")
    assert "legacy compatibility routes" in text
    response = create_app({"TESTING": True}).test_client().post("/compute/start", json={})
    assert response.status_code == 400


def test_preflight_command_passes():
    run = subprocess.run(["python", "scripts/preflight_checks.py"], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
