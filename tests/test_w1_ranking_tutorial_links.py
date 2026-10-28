"""W1 regression checks for ranking tutorial served links."""
from html.parser import HTMLParser
from pathlib import Path

import pytest

from app import create_app

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "docs" / "modules" / "ranking_tutorial_side_by_side.html"
STATIC = ROOT / "website" / "modules" / "ranking" / "tutorial" / "index.html"
REMOVED_REPOSITORY_HREFS = (
    "README.md",
    "cli_quickstart.md",
    "debugging.md",
    "criteria_balanced.json",
    "electre3/ranking.py",
    "test_evidence.py",
)


class _LinksAndIds(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "a" and values.get("href") is not None:
            self.hrefs.append(values["href"])


def _parse(path: Path) -> _LinksAndIds:
    parser = _LinksAndIds()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


@pytest.fixture
def client():
    return create_app({"TESTING": True, "SECRET_KEY": "w1-test"}).test_client()


@pytest.mark.parametrize("path", [SOURCE, STATIC])
def test_ranking_tutorial_uses_resolvable_source_reference_fragment(path):
    page = _parse(path)
    assert "source-references" in page.ids
    assert "#source-references" in page.hrefs
    assert all(not any(removed in href for removed in REMOVED_REPOSITORY_HREFS) for href in page.hrefs)


def test_ranking_tutorial_static_derivative_matches_authoritative_link_strategy():
    source = _parse(SOURCE)
    derivative = _parse(STATIC)
    assert "#source-references" in source.hrefs
    assert "#source-references" in derivative.hrefs
    assert derivative.ids.issuperset({"source-references"})


def test_ranking_tutorial_flask_route_and_fragment_resolve(client):
    response = client.get("/docs/modules/ranking/tutorial")
    assert response.status_code == 200
    page = _LinksAndIds()
    page.feed(response.get_data(as_text=True))
    assert "source-references" in page.ids
    assert "#source-references" in page.hrefs


@pytest.mark.parametrize(
    "path",
    [
        "/docs/modules/ranking/tutorial/",
        "/docs/modules/ranking/assets/missing.js",
        "/docs/modules/ranking/../../README.md",
    ],
)
def test_ranking_tutorial_invalid_nested_paths_remain_rejected(client, path):
    assert client.get(path, follow_redirects=False).status_code == 404
