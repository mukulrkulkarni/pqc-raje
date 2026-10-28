"""W3 resolver-aware contract checks for static, Flask, and document URLs."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from app import create_app
from app import _companion_website_url
from scripts.build_website import synchronize_generated_tree

ROOT = Path(__file__).parent.parent
WEBSITE = ROOT / "website"
DOCS = ROOT / "docs"
MODULES = {"config", "validate", "block", "accumulator", "ranking"}
ASSETS = {"theme.js", "highlight.js"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")


class _References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for attribute in ("href", "src", "action", "poster"):
            if values.get(attribute) is not None:
                self.refs.append((attribute, values[attribute] or ""))


def _classify(target: str) -> str:
    parsed = urlsplit(target)
    if parsed.scheme in {"http", "https", "mailto"}:
        return "external"
    if parsed.scheme or target.startswith("//"):
        return "unsafe"
    decoded = unquote(unquote(parsed.path))
    if "\\" in decoded or "\x00" in decoded:
        return "unsafe"
    return "local"


def _static_path(source: Path, target: str) -> Path:
    path = urlsplit(target).path
    relative = WEBSITE / path.lstrip("/") if path.startswith("/") else source.parent / path
    if not path or path.endswith("/"):
        relative /= "index.html"
    return relative.resolve()


def _check_static_html(path: Path) -> list[str]:
    parser = _References()
    parser.feed(path.read_text(encoding="utf-8"))
    errors = []
    for attribute, target in parser.refs:
        kind = _classify(target)
        if kind == "external":
            continue
        if kind != "local":
            errors.append(f"unsafe {attribute}: {target}")
            continue
        target_path, _, fragment = target.partition("#")
        if not target_path:
            if fragment and fragment not in parser.ids:
                errors.append(f"missing fragment: {target}")
            continue
        destination = _static_path(path, target)
        try:
            destination.relative_to(WEBSITE.resolve())
        except ValueError:
            errors.append(f"escapes website: {target}")
            continue
        if not destination.is_file():
            errors.append(f"missing {attribute}: {target}")
            continue
        if fragment and destination.suffix == ".html":
            other = _References()
            other.feed(destination.read_text(encoding="utf-8"))
            if fragment not in other.ids:
                errors.append(f"missing fragment: {target}")
    return errors


def _check_markdown(path: Path) -> list[str]:
    errors = []
    for target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
        if _classify(target) == "external":
            continue
        if _classify(target) != "local":
            errors.append(f"unsafe markdown target: {target}")
            continue
        target_path = urlsplit(target).path
        if target_path and not (path.parent / target_path).resolve().is_file():
            errors.append(f"missing markdown target: {target}")
    return errors


def _client():
    return create_app({"TESTING": True, "SECRET_KEY": "w3-test", "COMPANION_WEBSITE_URL": "http://127.0.0.1:43127"}).test_client()


def test_manifest_defines_namespaces_examples_and_generated_ownership() -> None:
    manifest = json.loads((DOCS / "link-contract.json").read_text(encoding="utf-8"))
    assert manifest["version"] == 1
    assert manifest["destinations"]["examples"]["static"] == "/examples/index.html"
    assert "scripts/build_website.py" in manifest["ownership"]["website/examples/assets_priority/"]
    assert "/docs/modules/<module>/tutorial" in manifest["namespaces"]["flask"]["canonical"]


def test_every_static_html_reference_resolves_or_is_classified_external() -> None:
    errors = []
    for page in WEBSITE.rglob("*.html"):
        if "_includes" not in page.parts:
            errors.extend(f"{page.relative_to(ROOT)}: {error}" for error in _check_static_html(page))
    assert errors == []


def test_generated_tutorials_and_markdown_documents_have_safe_links() -> None:
    tutorials = list(WEBSITE.glob("modules/*/tutorial/index.html"))
    assert len(tutorials) == len(MODULES)
    assert all(_check_static_html(tutorial) == [] for tutorial in tutorials)
    assert _check_markdown(DOCS / "decisions" / "w3-link-contract-notes.md") == []


@pytest.mark.parametrize("path", [
    "/", "/app/", "/docs/modules", "/docs/modules/ranking", "/docs/modules/ranking/tutorial",
    "/docs/modules/ranking/assets/theme.js",
])
def test_flask_canonical_routes_resolve(path: str) -> None:
    assert _client().get(path).status_code == 200


@pytest.mark.parametrize("path", [
    "/docs/modules/", "/docs/modules/ranking/", "/docs/modules/ranking/tutorial/",
    "/docs/modules/ranking/assets/theme.js/",
])
def test_flask_trailing_slash_variants_are_not_canonical(path: str) -> None:
    assert _client().get(path, follow_redirects=False).status_code == 404


@pytest.mark.parametrize("path", [
    "/docs/modules/ranking/../../README.md",
    "/docs/modules/%2e%2e%2f%2e%2e%2fREADME.md",
    "/docs/modules/ranking/assets/%252e%252e%252ftheme.js",
    "/docs/modules/ranking/assets/..\\theme.js",
])
def test_flask_rejects_traversal_and_encoded_paths(path: str) -> None:
    assert _client().get(path, follow_redirects=False).status_code == 404


@pytest.mark.parametrize("value", [
    "https://trusted.test@evil.test", "https://trusted.test/#next", "//evil.test", "https://trusted.test/path",
])
def test_companion_origin_rejects_open_redirect_forms(value: str) -> None:
    with pytest.raises(ValueError, match="COMPANION_WEBSITE_URL"):
        _companion_website_url(value)


def test_examples_destination_uses_only_configured_companion_origin() -> None:
    response = _client().get("/")
    assert b'href="http://127.0.0.1:43127/examples/index.html">Examples</a>' in response.data
    assert b"?next=" not in response.data


def test_external_links_are_classified_without_network_access() -> None:
    assert _classify("https://example.test/docs") == "external"
    assert _classify("mailto:team@example.test") == "external"
    assert _classify("//example.test/path") == "unsafe"


def test_resolver_reports_broken_link_fragment_and_traversal(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_text('<a href="missing.html">x</a><a href="#missing">y</a><a href="../secret.html">z</a>', encoding="utf-8")
    original = WEBSITE
    try:
        globals()["WEBSITE"] = tmp_path
        assert _check_static_html(page) == [
            "missing href: missing.html", "missing fragment: #missing", "escapes website: ../secret.html"
        ]
    finally:
        globals()["WEBSITE"] = original


def test_generated_output_deletion_removes_stale_asset(tmp_path: Path) -> None:
    source, destination = tmp_path / "source", tmp_path / "website" / "examples"
    source.mkdir()
    (source / "current.json").write_text("{}", encoding="utf-8")
    destination.mkdir(parents=True)
    (destination / "stale.json").write_text("{}", encoding="utf-8")
    synchronize_generated_tree(source, destination)
    assert (destination / "current.json").exists()
    assert not (destination / "stale.json").exists()
