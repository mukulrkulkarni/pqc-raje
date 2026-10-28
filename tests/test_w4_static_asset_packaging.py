"""W4 source-of-truth static asset packaging contract."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import build_website
from tests.test_w3_link_contract import _check_static_html

ROOT = Path(__file__).parent.parent
MANIFEST = ROOT / "docs" / "static-asset-manifest.json"
WEBSITE = ROOT / "website"
EXAMPLES = ROOT / "examples"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_the_exact_source_of_truth_for_published_example_files() -> None:
    manifest = _manifest()
    assert manifest["version"] == 1
    assert manifest["ownership"]["generator"] == "scripts/build_website.py"
    for asset in manifest["assets"]:
        source = EXAMPLES / asset["source"]
        published = WEBSITE / "examples" / asset["target"]
        expected = set(asset["files"])
        assert {path.name for path in source.iterdir()} == expected
        assert {path.name for path in published.iterdir()} == expected
        for name in expected:
            assert (source / name).read_bytes() == (published / name).read_bytes()


def test_examples_landing_links_to_all_user_facing_manifest_files() -> None:
    page = (WEBSITE / "examples" / "index.html").read_text(encoding="utf-8")
    asset = _manifest()["assets"][0]
    for name in ("README.md", "criteria.json", "matrix_with_headers.csv", "ranking.txt"):
        assert f'/examples/{asset["target"]}/{name}' in page
    assert _check_static_html(WEBSITE / "examples" / "index.html") == []


def test_nested_static_examples_child_paths_and_fragment_resolve() -> None:
    child = WEBSITE / "examples" / "assets_priority" / "criteria.json"
    assert child.is_file()
    errors = _check_static_html(WEBSITE / "examples" / "index.html")
    assert errors == []


def test_resolver_rejects_nested_missing_targets_and_missing_fragments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    page = tmp_path / "examples" / "index.html"
    page.parent.mkdir()
    page.write_text('<a href="assets_priority/missing.csv">missing</a><a href="#missing">fragment</a>', encoding="utf-8")
    monkeypatch.setattr("tests.test_w3_link_contract.WEBSITE", tmp_path)
    assert _check_static_html(page) == ["missing href: assets_priority/missing.csv", "missing fragment: #missing"]


def test_packaging_rejects_missing_source_extra_file_and_invalid_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source_root, website_root = tmp_path / "examples", tmp_path / "website"
    source = source_root / "priority"
    source.mkdir(parents=True)
    (source / "approved.txt").write_text("approved", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"version": 1, "ownership": {"source": "examples/", "published": "website/examples/", "generator": "scripts/build_website.py"}, "assets": [{"id": "priority", "source": "priority", "target": "priority", "files": ["approved.txt"]}]}), encoding="utf-8")
    monkeypatch.setattr(build_website, "EXAMPLES", source_root)
    monkeypatch.setattr(build_website, "WEBSITE", website_root)
    monkeypatch.setattr(build_website, "STATIC_ASSET_MANIFEST", manifest)
    build_website.copy_examples()
    assert (website_root / "examples" / "priority" / "approved.txt").is_file()
    (source / "unexpected.txt").write_text("not approved", encoding="utf-8")
    with pytest.raises(ValueError, match="does not match source"):
        build_website.copy_examples()
    manifest.write_text(json.dumps({"version": 1, "ownership": {}, "assets": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="ownership"):
        build_website.load_static_asset_manifest()


def test_packaging_removes_stale_output_and_preserves_destination_after_failure(tmp_path: Path) -> None:
    source, destination = tmp_path / "source", tmp_path / "published" / "priority"
    source.mkdir()
    (source / "current.txt").write_text("current", encoding="utf-8")
    destination.mkdir(parents=True)
    (destination / "stale.txt").write_text("stale", encoding="utf-8")
    build_website.synchronize_generated_tree(source, destination)
    assert (destination / "current.txt").read_text(encoding="utf-8") == "current"
    assert not (destination / "stale.txt").exists()
    with pytest.raises(FileNotFoundError):
        build_website.synchronize_generated_tree(tmp_path / "missing", destination)
    assert (destination / "current.txt").read_text(encoding="utf-8") == "current"


@pytest.mark.parametrize("bad", ["../escape", "nested/path", "nested\\path", "..", ""])
def test_manifest_rejects_invalid_source_target_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad: str) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"version": 1, "ownership": {"source": "examples/", "published": "website/examples/", "generator": "scripts/build_website.py"}, "assets": [{"id": "priority", "source": bad, "target": "priority", "files": ["safe.txt"]}]}), encoding="utf-8")
    monkeypatch.setattr(build_website, "STATIC_ASSET_MANIFEST", manifest)
    with pytest.raises(ValueError, match="source or target"):
        build_website.load_static_asset_manifest()
