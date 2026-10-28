"""Structural UI and CSP tests for server-rendered active /app templates."""
import re
from pathlib import Path

import pytest

from app import CSP_APP, CSP_DOCS, create_app

TEMPLATE_DIR = Path(__file__).parent.parent / "app" / "templates"
ACTIVE_TEMPLATES = tuple(TEMPLATE_DIR / name for name in (
    "app_input.html", "app_matrix.html", "app_preview.html", "app_results.html",
))


@pytest.fixture
def client():
    return create_app({"TESTING": True, "SECRET_KEY": "active-template-test"}).test_client()


@pytest.mark.parametrize("template_path", ACTIVE_TEMPLATES, ids=lambda path: path.name)
def test_active_template_links_local_stylesheet_and_declares_viewport(template_path):
    content = template_path.read_text(encoding="utf-8")
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in content
    assert "url_for('static', filename='style.css')" in content
    # The workflow may link to the companion loopback website; it must not load remote assets.
    assert "https://" not in content
    assert 'src="http://' not in content
    assert re.sub(r'href="http://127\.0\.0\.1:\d+/', 'href="/', content).count('href="http://') == 0


@pytest.mark.parametrize("template_path", ACTIVE_TEMPLATES, ids=lambda path: path.name)
def test_active_template_has_semantic_main_and_no_script_or_inline_handlers(template_path):
    content = template_path.read_text(encoding="utf-8")
    assert "<main" in content and "</main>" in content
    assert "<script" not in content.lower()
    assert not re.search(r"\son[a-z]+\s*=", content, flags=re.IGNORECASE)


@pytest.mark.parametrize("template_path", ACTIVE_TEMPLATES, ids=lambda path: path.name)
def test_active_template_uses_html5_document_structure(template_path):
    content = template_path.read_text(encoding="utf-8")
    assert content.lower().startswith("<!doctype html>")
    assert '<html lang="en">' in content
    assert "<title>" in content


@pytest.mark.parametrize("template_path", (TEMPLATE_DIR / "app_preview.html", TEMPLATE_DIR / "app_results.html"), ids=lambda path: path.name)
def test_active_tables_have_scoped_headers_and_responsive_data_labels(template_path):
    content = template_path.read_text(encoding="utf-8")
    assert '<th scope="col">' in content
    assert "data-label=" in content


def test_app_css_asset_is_served_without_external_network(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert b"@media" in response.data
    assert "text/css" in response.headers["Content-Type"]


@pytest.mark.parametrize("route", ("/app", "/app/"))
def test_app_routes_use_exact_script_free_csp(client, route):
    response = client.get(route)
    assert response.status_code in {200, 308}
    if response.status_code == 308:
        response = client.get(response.headers["Location"])
    assert response.headers["Content-Security-Policy"] == CSP_APP
    assert "script-src" not in CSP_APP


@pytest.mark.parametrize("route", ("/", "/docs/modules/config"))
def test_docs_routes_use_exact_docs_csp(client, route):
    response = client.get(route)
    assert response.status_code == 200
    assert response.headers["Content-Security-Policy"] == CSP_DOCS
    assert "script-src 'self'" in CSP_DOCS
    assert "script-src 'unsafe-inline'" not in CSP_DOCS
