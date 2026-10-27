"""D3 P0/P1 page-application documentation contract tests."""
from pathlib import Path
import re

import pytest

from app import create_app


ROOT = Path(__file__).parent.parent
RUNBOOK = ROOT / "docs" / "runbook" / "debugging.md"
QUICKSTART = ROOT / "docs" / "tutorials" / "cli_quickstart.md"
GETTING_STARTED = ROOT / "docs" / "GETTING_STARTED.html"
WEBSITE_INDEX = ROOT / "website" / "index.html"


@pytest.fixture
def client():
    return create_app({"TESTING": True, "SECRET_KEY": "d3-p0p1-test"}).test_client()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_runbook_distinguishes_supported_and_legacy_confirmation_statuses(client):
    """Positive and negative workflow gates use their distinct documented status codes."""
    runbook = _read(RUNBOOK)
    assert "Supported app computation needs preview and confirmation (HTTP 400)" in runbook
    assert "POST /app/compute" in runbook
    assert "legacy compatibility routes" in runbook
    assert "app/templates/preview.html" in runbook
    assert "app/templates/config.html" in runbook
    assert "POST /compute/start` returns HTTP 403" in runbook

    assert client.post("/app/compute", data={"confirm_compute": "yes"}).status_code == 400
    assert client.post(
        "/compute/start", json={"upload_id": "missing", "criteria": [{"name": "A"}]}
    ).status_code == 403


def test_reconciliation_keeps_direct_and_converted_labels_distinct():
    """Direct CSV and converted NumPy descriptions agree without treating labels as ranks."""
    for path in (QUICKSTART, GETTING_STARTED, WEBSITE_INDEX):
        text = _read(path)
        normalized = text.lower()
        assert "direct csv" in normalized
        assert "converted numpy" in normalized
        assert "B" in text and "A" in text and "C" in text
        assert "1" in text and "0" in text and "2" in text
        assert "one-based rank positions" in text
        assert "same ordering" in text


def test_reconciliation_preserves_tie_and_browser_evidence_boundaries():
    """Edge-case order and browser evidence remain appropriately limited."""
    quickstart = _read(QUICKSTART)
    getting_started = _read(GETTING_STARTED).lower()
    assert "no documented stable order" in quickstart
    assert "browser reflow" in getting_started
    assert "browser zoom" in getting_started
    assert "screen-reader" in getting_started
    assert "unverified" in getting_started


def test_user_facing_html_local_links_have_targets():
    """Internal navigation links resolve to a local file or in-page target."""
    for path in (GETTING_STARTED, WEBSITE_INDEX):
        text = _read(path)
        ids = set(re.findall(r'\bid="([^"]+)"', text))
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith("#"):
                assert href[1:] in ids, f"{path}: unresolved in-page link {href}"
            elif href.startswith(("http://", "https://")):
                pytest.fail(f"{path}: external link is outside this reproducibility contract: {href}")


def test_reproducibility_commands_and_sources_are_present():
    """The approved commands and source citations remain inspectable."""
    draft = _read(ROOT / "docs" / "decisions" / "d3-p0p1-draft.md")
    assert "set PYTHONPATH=." in draft
    assert "scripts/convert_matrix_csv.py" in draft
    assert "electre3/data.py::load_input" in draft
    assert "electre3/ranking.py::compute_ranking" in draft
    assert "app/routes/workflow.py" in draft
