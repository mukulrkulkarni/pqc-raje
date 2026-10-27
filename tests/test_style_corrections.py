"""Static evidence for the approved documentation styling-correction chunk."""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
DOC_MODULES = ROOT / "docs" / "modules"
WEBSITE_MODULES = ROOT / "website" / "modules"
TUTORIALS = sorted(DOC_MODULES.glob("*_tutorial_side_by_side.html"))
GENERATED = sorted(WEBSITE_MODULES.glob("*/tutorial/index.html"))


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        for name in ("href", "src"):
            if values.get(name):
                self.links.append(values[name])


def _parse(path: Path) -> _Links:
    parser = _Links()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def _local_errors(path: Path, root: Path) -> list[str]:
    parsed = _parse(path)
    errors = []
    for target in parsed.links:
        if target.startswith(("http:", "https:", "mailto:", "data:")):
            continue
        pathname, marker, fragment = target.partition("#")
        if pathname.startswith("/"):
            # Flask routes do not have a static filesystem equivalent.
            continue
        destination = path.parent / pathname if pathname else path
        if pathname and not destination.is_file():
            errors.append(f"missing local target: {path.relative_to(root)} -> {target}")
            continue
        if marker:
            target_ids = _parse(destination).ids
            if fragment not in target_ids:
                errors.append(f"missing fragment: {path.relative_to(root)} -> {target}")
    return errors


def _normalized_generated_source(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    text = text.replace('src="assets/theme.js"', 'src="../../assets/theme.js"')
    text = text.replace('src="assets/highlight.js"', 'src="../../assets/highlight.js"')
    for source_link, generated_link in {
        '../../README.md': '../../../../README.md',
        '../tutorials/': '../../../../docs/tutorials/',
        '../runbook/': '../../../../docs/runbook/',
        '../../examples/': '../../../../examples/',
        '../../electre3/': '../../../../electre3/',
        '../../tests/': '../../../../tests/',
    }.items():
        text = text.replace(f'href="{source_link}', f'href="{generated_link}')
    nav = (
        '<nav class="primary-nav" aria-label="Primary">'
        '<a href="/index.html">Getting Started</a>'
        '<a href="/app/index.html">App</a>'
        '<a href="/modules/index.html" aria-current="page">Tutorials</a>'
        '<a href="http://localhost:5000/">Flask home</a>'
        '<a href="http://localhost:5000/docs/modules">Flask modules</a>'
        '</nav>'
    )
    return re.sub(r"(<body(?:\s|>)[^>]*>)", r"\1\n" + nav, text, count=1, flags=re.I)


def test_all_owned_tutorials_use_mk_tii_tokens_and_safe_no_js_fallback() -> None:
    assert TUTORIALS
    for path in TUTORIALS:
        text = path.read_text(encoding="utf-8")
        for token in ("Arial,sans-serif", "--accent:#6400ff", "#253746", "#7eddd3", "--radius:8px"):
            assert token in text, f"{path}: missing {token}"
        assert ".row:target" in text, f"{path}: no hash fallback"
        assert 'role="button"' in text, f"{path}: no keyboard-row semantics"
        assert "Generated primary navigation contract" in text


def test_landing_pages_use_mk_tii_tokens_and_active_navigation() -> None:
    pages = [DOC_MODULES / "index.html", *WEBSITE_MODULES.glob("*/index.html")]
    for path in pages:
        text = path.read_text(encoding="utf-8")
        for token in ("Arial,sans-serif", "#6400ff", "#253746", "#7eddd3"):
            assert token in text, f"{path}: missing {token}"
        assert "aria-current=\"page\"" in text
        assert ":focus-visible" in text


def test_owned_html_local_links_and_fragments_resolve() -> None:
    pages = [*TUTORIALS, DOC_MODULES / "index.html", *WEBSITE_MODULES.rglob("*.html")]
    errors = [error for page in pages for error in _local_errors(page, ROOT)]
    for page in WEBSITE_MODULES.glob("*/tutorial/index.html"):
        text = page.read_text(encoding="utf-8")
        assert (WEBSITE_MODULES / "assets" / "theme.js").is_file()
        assert (WEBSITE_MODULES / "assets" / "highlight.js").is_file()
        assert 'src="../../assets/theme.js"' in text
        assert 'src="../../assets/highlight.js"' in text
    assert errors == []


def test_link_checker_detects_missing_local_target_and_fragment(tmp_path: Path) -> None:
    page = tmp_path / "page.html"
    page.write_text('<a href="missing.html">x</a><a href="#missing">y</a>', encoding="utf-8")
    assert _local_errors(page, tmp_path) == [
        "missing local target: page.html -> missing.html",
        "missing fragment: page.html -> #missing",
    ]


def test_math_meaning_has_no_remote_renderer_dependency() -> None:
    pages = [ROOT / "docs" / "GETTING_STARTED.html", *TUTORIALS]
    for path in pages:
        text = path.read_text(encoding="utf-8")
        assert not re.search(r'<script[^>]+src="https?://[^\"]*(?:mathjax|katex)', text, re.I)
    getting_started = (ROOT / "docs" / "GETTING_STARTED.html").read_text(encoding="utf-8")
    assert any(marker in getting_started for marker in ("<var>Φ</var>", "Σ<sub>", "0 ≤ q ≤ p ≤ v"))


def test_generator_output_matches_authoritative_sources() -> None:
    assert len(GENERATED) == 5
    for generated in GENERATED:
        module = generated.parents[1].name
        source = DOC_MODULES / f"{module}_tutorial_side_by_side.html"
        assert source.is_file(), f"missing source for {generated}"
        assert generated.read_text(encoding="utf-8") == _normalized_generated_source(source)


def test_generator_is_idempotent_and_owned_outputs_change_only_from_sources() -> None:
    command = [sys.executable, "scripts/build_website.py"]
    first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in GENERATED}
    second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in GENERATED}
    assert after == before


def test_generator_rejects_missing_body_and_incomplete_primary_navigation() -> None:
    from scripts.build_website import inject_primary_nav

    with pytest.raises(ValueError, match="missing <body>"):
        inject_primary_nav("<html><bodyguard></bodyguard></html>", "/modules/x/tutorial/")
    with pytest.raises(ValueError, match="lacks required links"):
        inject_primary_nav('<body><nav aria-label="Primary"></nav></body>', "/modules/x/tutorial/")
