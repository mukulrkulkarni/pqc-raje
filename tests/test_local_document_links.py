"""Focused stdlib checks for remediation decision-document local links and fragments."""
import re
from pathlib import Path

import pytest

DOCS = Path(__file__).parent.parent / "docs" / "decisions"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _fragment_id(heading: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", heading.lower()).replace(" ", "-")


def _check_links(source: Path) -> list[str]:
    errors = []
    content = source.read_text(encoding="utf-8")
    for target in MARKDOWN_LINK.findall(content):
        if "://" in target or target.startswith("mailto:"):
            continue
        path_part, _, fragment = target.partition("#")
        destination = source.parent / path_part if path_part else source
        if not destination.is_file():
            errors.append(f"missing local target: {target}")
            continue
        if fragment and destination.suffix == ".md":
            anchors = {_fragment_id(text) for text in HEADING.findall(destination.read_text(encoding="utf-8"))}
            if fragment not in anchors:
                errors.append(f"missing fragment: {target}")
    return errors


@pytest.mark.parametrize("name", [
    "dynamic-elements-meeting-report.md",
    "dynamic-elements-remediation-notes.md",
    "d7-documentation-notes.md",
])
def test_remediation_decision_links_and_fragments_resolve(name):
    assert _check_links(DOCS / name) == []


def test_link_checker_reports_missing_local_file_and_fragment(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("[file](missing.md) [fragment](target.md#missing)", encoding="utf-8")
    (tmp_path / "target.md").write_text("# Present\n", encoding="utf-8")
    assert _check_links(source) == [
        "missing local target: missing.md",
        "missing fragment: target.md#missing",
    ]


def test_link_checker_ignores_external_and_anchor_only_links(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("# Local\n[external](https://example.test) [anchor](#local)", encoding="utf-8")
    assert _check_links(source) == []
