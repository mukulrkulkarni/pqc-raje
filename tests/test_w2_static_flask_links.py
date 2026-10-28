"""W2 served-link checks for the static website and Flask documentation vocabularies."""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from app import create_app

ROOT = Path(__file__).parent.parent


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get(url: str) -> tuple[int, bytes]:
    with urlopen(url, timeout=2) as response:
        return response.status, response.read()


def _wait(url: str) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            if _get(url)[0] == 200:
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"service did not respond at {url}")


@pytest.fixture
def local_services():
    website_port, app_port = _free_port(), _free_port()
    while app_port == website_port:
        app_port = _free_port()
    env = os.environ | {"WEBSITE_PORT": str(website_port), "APP_PORT": str(app_port)}
    process = subprocess.Popen(
        [sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    try:
        _wait(f"http://127.0.0.1:{website_port}/")
        _wait(f"http://127.0.0.1:{app_port}/")
        yield website_port, app_port
    finally:
        if process.poll() is None:
            process.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGINT))
            process.communicate(timeout=5)


@pytest.mark.parametrize("path", [
    "/", "/index.html", "/modules/", "/modules/ranking/tutorial/",
    "/reference/", "/examples/", "/examples/index.html",
    "/examples/assets_priority/criteria.json", "/modules/assets/theme.js",
])
def test_static_served_root_nested_tutorial_reference_examples_and_assets(local_services, path):
    website_port, _ = local_services
    status, _ = _get(f"http://127.0.0.1:{website_port}{path}")
    assert status == 200


def test_static_examples_landing_has_committed_asset_links_and_fragment(local_services):
    website_port, _ = local_services
    _, landing = _get(f"http://127.0.0.1:{website_port}/")
    assert b'href="/examples/index.html"' in landing
    _, example = _get(f"http://127.0.0.1:{website_port}/examples/index.html")
    assert b"/examples/assets_priority/criteria.json" in example
    assert b"/examples/assets_priority/matrix_with_headers.csv" in example
    assert b"/examples/assets_priority/ranking.txt" in example
    assert b'href="/index.html"' in landing


@pytest.mark.parametrize("path", ["/missing", "/examples/assets_priority/missing.csv", "/modules/nope/"])
def test_static_intentional_missing_paths_remain_404(local_services, path):
    website_port, _ = local_services
    with pytest.raises(HTTPError) as error:
        _get(f"http://127.0.0.1:{website_port}{path}")
    assert error.value.code == 404


def test_static_fragment_is_a_client_side_reference_only(local_services):
    website_port, _ = local_services
    status, body = _get(f"http://127.0.0.1:{website_port}/index.html#cli")
    assert status == 200
    assert b'<section id="cli">' in body


@pytest.fixture
def client():
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "w2-test",
        "COMPANION_WEBSITE_URL": "http://127.0.0.1:43127",
    }).test_client()


@pytest.mark.parametrize("path", ["/", "/app/", "/docs/modules", "/docs/modules/ranking/tutorial"])
def test_flask_route_vocabulary_remains_available(client, path):
    assert client.get(path).status_code == 200


def test_flask_landing_and_app_expose_static_examples_destination(client):
    expected = b'http://127.0.0.1:43127/examples/index.html'
    assert expected in client.get("/").data
    assert expected in client.get("/app/").data


@pytest.mark.parametrize("path", ["/examples/index.html", "/docs/modules/missing", "/docs/modules/ranking/tutorial/"])
def test_flask_intentional_unsupported_routes_remain_404(client, path):
    assert client.get(path, follow_redirects=False).status_code == 404
