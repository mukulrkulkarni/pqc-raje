"""Regression tests for the bounded W2 recovery."""
from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app
from scripts.build_website import synchronize_generated_tree


def test_flask_examples_link_uses_configured_companion_origin() -> None:
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "w2-recovery-test",
        "COMPANION_WEBSITE_URL": "http://127.0.0.1:43127",
    })
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b'href="http://127.0.0.1:43127/examples/index.html">Examples</a>' in response.data
    assert b":8000/examples/index.html" not in response.data


@pytest.mark.parametrize("value", ["/examples", "ftp://localhost", "http://host/path", "http://host/?q=1"])
def test_flask_rejects_unsafe_companion_website_destination(value: str) -> None:
    with pytest.raises(ValueError, match="COMPANION_WEBSITE_URL"):
        create_app({"TESTING": True, "COMPANION_WEBSITE_URL": value})


def test_synchronize_generated_tree_removes_stale_output(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "generated" / "assets_priority"
    source.mkdir()
    (source / "current.txt").write_text("current", encoding="utf-8")
    destination.mkdir(parents=True)
    (destination / "stale.txt").write_text("stale", encoding="utf-8")

    synchronize_generated_tree(source, destination)

    assert (destination / "current.txt").read_text(encoding="utf-8") == "current"
    assert not (destination / "stale.txt").exists()


def test_synchronize_generated_tree_preserves_existing_output_on_missing_source(tmp_path: Path) -> None:
    destination = tmp_path / "generated" / "assets_priority"
    destination.mkdir(parents=True)
    existing = destination / "previous.txt"
    existing.write_text("keep", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Missing committed example directory"):
        synchronize_generated_tree(tmp_path / "missing", destination)

    assert existing.read_text(encoding="utf-8") == "keep"


def test_synchronize_generated_tree_handles_empty_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "generated" / "assets_priority"
    source.mkdir()
    destination.mkdir(parents=True)
    (destination / "stale.txt").write_text("stale", encoding="utf-8")

    synchronize_generated_tree(source, destination)

    assert destination.is_dir()
    assert list(destination.iterdir()) == []
