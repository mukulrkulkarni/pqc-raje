"""D7 static/Flask route reconciliation checks."""
from pathlib import Path

from app import create_app


ROOT = Path(__file__).parent.parent
WEBSITE = ROOT / "website"
REFERENCE = WEBSITE / "reference" / "index.html"


def test_reference_page_has_current_and_planned_labels() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert "Current routes" in text
    assert "Planned hosting" in text
    assert "<script" not in text.lower()


def test_static_navigation_uses_static_paths() -> None:
    for path in (WEBSITE / "index.html", WEBSITE / "app" / "index.html", WEBSITE / "modules" / "index.html"):
        assert 'href="/reference/index.html"' in path.read_text(encoding="utf-8")
    assert REFERENCE.is_file()


def test_generated_tutorial_ownership_is_unchanged() -> None:
    source = ROOT / "docs" / "modules" / "config_tutorial_side_by_side.html"
    output = WEBSITE / "modules" / "config" / "tutorial" / "index.html"
    assert "Generated primary navigation contract" in source.read_text(encoding="utf-8")
    assert output.read_text(encoding="utf-8").endswith("</html>\n")


def test_flask_docs_routes_remain_separate_from_static_paths() -> None:
    client = create_app({"TESTING": True}).test_client()
    assert client.get("/docs/modules").status_code == 200
    assert client.get("/docs/modules/config/tutorial").status_code == 200
    assert client.get("/docs/modules/config/../../app.py").status_code == 404


def test_d6_sources_remain_repository_owned() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert "docs/tutorials/cli_quickstart.md" in text
    assert "docs/runbook/debugging.md" in text
    assert not (WEBSITE / "docs" / "tutorials" / "cli_quickstart.md").exists()
