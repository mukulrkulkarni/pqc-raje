"""Start the companion website and Flask app with one local command.

Usage:
    python scripts/dev_local.py

Environment:
    WEBSITE_PORT  Website loopback port (default: 8000).
    APP_PORT      Flask loopback port (default: 5000).

The launcher binds both ports before it prints URLs. Press Ctrl+C to stop both
servers. It never enables Flask's reloader, so it does not create child processes.
"""

from __future__ import annotations

import os
import queue
import signal
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import BaseServer
from typing import Callable, Protocol

ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = ROOT / "website" / "app"
HOST = "127.0.0.1"


class ServeForever(Protocol):
    def serve_forever(self) -> None: ...
    def shutdown(self) -> None: ...
    def server_close(self) -> None: ...


class WebsiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(WEBSITE_DIR), **kwargs)


def _port(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer between 1 and 65535; got {raw!r}") from exc
    if not 1 <= value <= 65535:
        raise ValueError(f"{name} must be between 1 and 65535; got {value}")
    return value


def _website_server(port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((HOST, port), WebsiteHandler)


def _app_server(port: int) -> BaseServer:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from app import create_app
    from werkzeug.serving import make_server

    return make_server(HOST, port, create_app({"TESTING": False}), threaded=True)


def _close(server: ServeForever) -> None:
    try:
        server.shutdown()
    finally:
        server.server_close()


def run_launcher(
    website_port: int,
    app_port: int,
    website_factory: Callable[[int], ServeForever] = _website_server,
    app_factory: Callable[[int], ServeForever] = _app_server,
) -> int:
    """Run both services until interrupt or a service exits or fails."""
    if website_port == app_port:
        print("Configuration error: WEBSITE_PORT and APP_PORT must differ.", file=sys.stderr)
        return 2

    servers: list[tuple[str, ServeForever]] = []
    try:
        servers.append(("website", website_factory(website_port)))
        servers.append(("app", app_factory(app_port)))
    except OSError as exc:
        for _, server in servers:
            server.server_close()
        service = "website" if not servers else "app"
        print(f"Startup error: {service} port is unavailable: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        for _, server in servers:
            server.server_close()
        print(f"Startup error: cannot create services: {exc}", file=sys.stderr)
        return 1

    failures: queue.Queue[tuple[str, BaseException | None]] = queue.Queue()
    stop = threading.Event()

    def serve(name: str, server: ServeForever) -> None:
        try:
            server.serve_forever()
            if not stop.is_set():
                failures.put((name, None))
        except BaseException as exc:  # Surface thread failures to the launcher.
            if not stop.is_set():
                failures.put((name, exc))

    threads = [threading.Thread(target=serve, args=(name, server), name=f"dev-local-{name}") for name, server in servers]
    for thread in threads:
        thread.start()

    print(f"Website: http://{HOST}:{website_port}/", flush=True)
    print(f"App:     http://{HOST}:{app_port}/app/", flush=True)
    print("Press Ctrl+C to stop both services.", flush=True)

    previous_handler = signal.getsignal(signal.SIGINT)
    break_signal = getattr(signal, "SIGBREAK", None)
    previous_break_handler = signal.getsignal(break_signal) if break_signal is not None else None

    def request_stop(_signum: int, _frame: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    if break_signal is not None:
        signal.signal(break_signal, request_stop)
    result = 0
    try:
        while not stop.wait(0.05):
            try:
                name, failure = failures.get_nowait()
            except queue.Empty:
                continue
            detail = "stopped unexpectedly" if failure is None else f"failed: {failure}"
            print(f"Runtime error: {name} service {detail}.", file=sys.stderr)
            result = 1
            break
    finally:
        stop.set()
        signal.signal(signal.SIGINT, previous_handler)
        if break_signal is not None:
            signal.signal(break_signal, previous_break_handler)
        for _, server in servers:
            _close(server)
        for thread in threads:
            thread.join(timeout=2)
        if any(thread.is_alive() for thread in threads):
            print("Shutdown error: a service thread did not stop.", file=sys.stderr)
            result = 1
    return result


def main() -> int:
    try:
        return run_launcher(_port("WEBSITE_PORT", 8000), _port("APP_PORT", 5000))
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
