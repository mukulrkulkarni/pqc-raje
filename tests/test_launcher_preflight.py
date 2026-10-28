"""Launcher preflight and lifecycle failure tests."""
from __future__ import annotations
import os
import socket
import subprocess
import sys
import threading
from pathlib import Path
import pytest
from scripts import dev_local
from scripts.launcher_health import health_errors
from scripts.launcher_preflight import root_errors
from tests.launcher_test_support import free_port
ROOT = Path(__file__).parent.parent

def test_occupied_port_reports_owner_before_startup_urls() -> None:
    occupied, app_port = free_port(), free_port()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", occupied)); listener.listen()
        result = subprocess.run([sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=os.environ | {"WEBSITE_PORT": str(occupied), "APP_PORT": str(app_port)}, capture_output=True, text=True, timeout=5)
    assert result.returncode == 2 and "website port is unavailable: port" in result.stderr and "PID" in result.stderr and "Website:" not in result.stdout

@pytest.mark.parametrize("value", ["nope", "0", "65536"])
def test_invalid_port_configuration_is_deterministic(value: str) -> None:
    result = subprocess.run([sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=os.environ | {"WEBSITE_PORT": value}, capture_output=True, text=True, timeout=5)
    assert result.returncode == 2 and "Configuration error: WEBSITE_PORT" in result.stderr

def test_matching_ports_are_rejected_without_creating_servers(capsys: pytest.CaptureFixture[str]) -> None:
    assert dev_local.run_launcher(8123, 8123) == 2; assert "must differ" in capsys.readouterr().err

def test_wrong_root_and_missing_file_diagnostics(tmp_path: Path) -> None:
    assert root_errors(tmp_path / "website", tmp_path / "app") == [f"missing required path: {tmp_path / 'website' / page}" for page in ("index.html", "examples/index.html", "modules/index.html", "reference/index.html")] + [f"missing required path: {tmp_path / 'app' / '__init__.py'}"]

def test_health_failure_reports_endpoint() -> None:
    class Reply:
        status = 404
        def __enter__(self): return self
        def __exit__(self, *_args): return False
    errors = health_errors(8123, 8456, lambda *_args, **_kwargs: Reply())
    assert len(errors) == 5 and all("health check failed:" in error and "returned 404" in error for error in errors)

class _FakeServer:
    def __init__(self, failure: BaseException | None = None) -> None: self.failure = failure; self.stopped = threading.Event(); self.closed = False
    def serve_forever(self) -> None:
        if self.failure: raise self.failure
        self.stopped.wait(2)
    def shutdown(self) -> None: self.stopped.set()
    def server_close(self) -> None: self.closed = True
