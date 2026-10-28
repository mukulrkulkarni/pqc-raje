"""Reusable local helpers for launcher tests."""
from __future__ import annotations

import socket
import time
from urllib.request import urlopen


def free_port() -> int:
    """Return a currently available loopback TCP port."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def distinct_ports() -> tuple[int, int]:
    """Return two different available loopback TCP ports."""
    first, second = free_port(), free_port()
    while second == first: second = free_port()
    return first, second


def wait_for(url: str) -> None:
    """Require a local endpoint to return HTTP 200 before timeout."""
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=.2) as response:
                if response.status == 200: return
        except OSError: time.sleep(.05)
    raise AssertionError(f"Service did not respond at {url}")
