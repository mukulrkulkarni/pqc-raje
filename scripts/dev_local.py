"""Start the companion website and Flask app with one local command."""
from __future__ import annotations

import sys
from pathlib import Path
from socketserver import BaseServer
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from scripts.launcher_cli import main as configured_main
from scripts.launcher_health import health_errors
from scripts.launcher_lifecycle import ServeForever, run_servers
from scripts.launcher_preflight import occupied_port, root_errors
from scripts.launcher_runtime import app_server, website_server
from scripts.launcher_startup import identity, servers

WEBSITE_DIR, APP_DIR, HOST = ROOT / "website", ROOT / "app", "127.0.0.1"


def _website_server(port: int) -> ServeForever: return website_server(WEBSITE_DIR, port)
def _app_server(port: int) -> BaseServer: return app_server(ROOT, port)


def _preflight(website_port: int, app_port: int) -> list[str]:
    errors = root_errors(WEBSITE_DIR, APP_DIR)
    for name, port in (("website", website_port), ("app", app_port)):
        if owner := occupied_port(port): errors.append(f"{name} port is unavailable: port {port} is occupied by PID {owner}.")
    return errors


def run_launcher(website_port: int, app_port: int, website_factory: Callable[[int], ServeForever] = _website_server, app_factory: Callable[[int], ServeForever] = _app_server) -> int:
    """Validate, start, identify, health-check, and stop both local services."""
    if website_port == app_port: print("Configuration error: WEBSITE_PORT and APP_PORT must differ.", file=sys.stderr); return 2
    if errors := _preflight(website_port, app_port): print("Startup error: " + " ".join(errors), file=sys.stderr); return 2
    active, result = servers(website_port, app_port, website_factory, app_factory)
    if result: return result
    def announce() -> None:
        errors = health_errors(website_port, app_port) if website_factory is _website_server and app_factory is _app_server else []
        if errors: raise RuntimeError(" ".join(errors))
        print(identity(ROOT, WEBSITE_DIR, APP_DIR, website_port, app_port), flush=True)
        print(f"Website: http://{HOST}:{website_port}/\nApp:     http://{HOST}:{app_port}/app/\nPress Ctrl+C to stop both services.", flush=True)
    try: return run_servers(active, announce)
    except RuntimeError as exc: print(f"Startup error: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(configured_main(run_launcher))
