"""Close local launcher servers and join their worker threads."""
from __future__ import annotations

import sys
import threading
from typing import Protocol

class Closable(Protocol):
    """Define the shutdown operations used by the launcher."""
    def shutdown(self) -> None: ...
    def server_close(self) -> None: ...

def close_servers(servers: list[tuple[str, Closable]], threads: list[threading.Thread]) -> int:
    """Stop every service and report threads that remain alive."""
    for _, server in servers:
        try: server.shutdown()
        finally: server.server_close()
    for thread in threads: thread.join(timeout=2)
    if any(thread.is_alive() for thread in threads):
        print("Shutdown error: a service thread did not stop.", file=sys.stderr)
        return 1
    return 0
