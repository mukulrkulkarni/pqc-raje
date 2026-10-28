"""Run launcher server threads and coordinated shutdown."""
from __future__ import annotations

import queue
import signal
import sys
import threading
from typing import Callable, Protocol
from scripts.launcher_shutdown import close_servers

class ServeForever(Protocol):
    """Define the server operations required by the launcher."""
    def serve_forever(self) -> None: ...
    def shutdown(self) -> None: ...
    def server_close(self) -> None: ...

def run_servers(servers: list[tuple[str, ServeForever]], announce: Callable[[], None]) -> int:
    """Serve until interruption or child failure, then close every server."""
    failures: queue.Queue[tuple[str, BaseException | None]] = queue.Queue(); stop = threading.Event()
    def serve(name: str, server: ServeForever) -> None:
        try:
            server.serve_forever()
            if not stop.is_set(): failures.put((name, None))
        except BaseException as exc:
            if not stop.is_set(): failures.put((name, exc))
    threads = [threading.Thread(target=serve, args=item, name=f"dev-local-{item[0]}") for item in servers]
    for thread in threads: thread.start()
    previous, result = signal.getsignal(signal.SIGINT), 0
    break_signal = getattr(signal, "SIGBREAK", None); previous_break = signal.getsignal(break_signal) if break_signal is not None else None
    signal.signal(signal.SIGINT, lambda *_args: stop.set())
    if break_signal is not None: signal.signal(break_signal, lambda *_args: stop.set())
    try:
        announce()
        while not stop.wait(.05):
            try: name, failure = failures.get_nowait()
            except queue.Empty: continue
            detail = "stopped unexpectedly" if failure is None else f"failed: {failure}"
            print(f"Runtime error: {name} service {detail}.", file=sys.stderr); result = 1; break
    finally:
        stop.set(); signal.signal(signal.SIGINT, previous)
        if break_signal is not None: signal.signal(break_signal, previous_break)
        result = max(result, close_servers(servers, threads))
    return result
