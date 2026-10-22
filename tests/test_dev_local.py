"""Launcher integration and lifecycle tests without manual long-running services."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.request import urlopen

import pytest

from scripts import dev_local

ROOT = Path(__file__).parent.parent


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _distinct_ports() -> tuple[int, int]:
    first = _free_port()
    second = _free_port()
    while second == first:
        second = _free_port()
    return first, second


def _wait_for(url: str) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=0.2) as response:
                assert response.status == 200
                return
        except OSError:
            time.sleep(0.05)
    raise AssertionError(f"Service did not respond at {url}")


def test_launcher_starts_both_services_prints_urls_and_stops_without_orphans() -> None:
    website_port, app_port = _distinct_ports()
    env = os.environ | {"WEBSITE_PORT": str(website_port), "APP_PORT": str(app_port)}
    process = subprocess.Popen(
        [sys.executable, "scripts/dev_local.py"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    try:
        startup = [process.stdout.readline().strip() for _ in range(3)]
        assert process.poll() is None, process.stderr.read()
        _wait_for(f"http://127.0.0.1:{website_port}/")
        _wait_for(f"http://127.0.0.1:{app_port}/app/")
        process.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGINT))
        remainder, stderr = process.communicate(timeout=5)
        stdout = "\n".join([*startup, remainder])
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()
    assert process.returncode == 0, stderr
    assert f"Website: http://127.0.0.1:{website_port}/" in stdout
    assert f"App:     http://127.0.0.1:{app_port}/app/" in stdout
    assert "Press Ctrl+C to stop both services." in stdout
    for port in (website_port, app_port):
        with socket.socket() as sock:
            assert sock.connect_ex(("127.0.0.1", port)) != 0


def test_port_conflict_fails_before_printing_startup_urls() -> None:
    occupied, app_port = _free_port(), _free_port()
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", occupied))
        listener.listen()
        env = os.environ | {"WEBSITE_PORT": str(occupied), "APP_PORT": str(app_port)}
        result = subprocess.run(
            [sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=env,
            capture_output=True, text=True, timeout=5,
        )
    assert result.returncode == 2
    assert "Startup error: website port is unavailable:" in result.stderr
    assert "Website:" not in result.stdout


@pytest.mark.parametrize("value", ["nope", "0", "65536"])
def test_invalid_port_configuration_is_deterministic(value: str) -> None:
    env = os.environ | {"WEBSITE_PORT": value}
    result = subprocess.run(
        [sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=env,
        capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 2
    assert "Configuration error: WEBSITE_PORT" in result.stderr


def test_matching_ports_are_rejected_without_creating_servers(capsys: pytest.CaptureFixture[str]) -> None:
    assert dev_local.run_launcher(8123, 8123) == 2
    assert "must differ" in capsys.readouterr().err


class _FakeServer:
    def __init__(self, failure: BaseException | None = None) -> None:
        self.failure = failure
        self.started = threading.Event()
        self.stopped = threading.Event()
        self.closed = False

    def serve_forever(self) -> None:
        self.started.set()
        if self.failure:
            raise self.failure
        self.stopped.wait(2)

    def shutdown(self) -> None:
        self.stopped.set()

    def server_close(self) -> None:
        self.closed = True


def test_child_failure_stops_peer_and_returns_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    failed = _FakeServer(RuntimeError("boom"))
    peer = _FakeServer()
    monkeypatch.setattr(dev_local.signal, "signal", lambda *_args: None)
    monkeypatch.setattr(dev_local.signal, "getsignal", lambda *_args: None)
    result = dev_local.run_launcher(8123, 8456, lambda _port: failed, lambda _port: peer)
    assert result == 1
    assert peer.stopped.is_set()
    assert failed.closed and peer.closed
    assert "Runtime error: website service failed: boom." in capsys.readouterr().err
