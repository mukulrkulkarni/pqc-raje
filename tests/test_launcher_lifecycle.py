"""Launcher child-failure lifecycle tests."""
from __future__ import annotations
import threading
import pytest
from scripts import dev_local

class FakeServer:
    """Minimal controllable server for launcher lifecycle tests."""
    def __init__(self, failure: BaseException | None = None) -> None:
        self.failure, self.stopped, self.closed = failure, threading.Event(), False
    def serve_forever(self) -> None:
        if self.failure: raise self.failure
        self.stopped.wait(2)
    def shutdown(self) -> None: self.stopped.set()
    def server_close(self) -> None: self.closed = True

def test_child_failure_stops_peer_and_returns_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    failed, peer = FakeServer(RuntimeError("boom")), FakeServer()
    monkeypatch.setattr(dev_local, "_preflight", lambda *_args: [])
    assert dev_local.run_launcher(8123, 8456, lambda _port: failed, lambda _port: peer) == 1
    assert peer.stopped.is_set() and failed.closed and peer.closed
    assert "Runtime error: website service failed: boom." in capsys.readouterr().err
