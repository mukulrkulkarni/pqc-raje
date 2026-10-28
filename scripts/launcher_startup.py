"""Create launcher server instances and report startup identity."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from socketserver import BaseServer
from typing import Callable

from scripts.launcher_lifecycle import ServeForever


def commit(root: Path) -> str:
    """Return the current local commit identifier when available."""
    result = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    return result.stdout.strip() or "unavailable"


def servers(website_port: int, app_port: int, website_factory: Callable, app_factory: Callable) -> tuple[list[tuple[str, ServeForever]], int]:
    """Create both services or return a deterministic startup result."""
    created: list[tuple[str, ServeForever]] = []
    try: created.extend((("website", website_factory(website_port)), ("app", app_factory(app_port))))
    except OSError as exc: print(f"Startup error: port is unavailable: {exc}", file=sys.stderr); return [], 2
    except Exception as exc: print(f"Startup error: cannot create services: {exc}", file=sys.stderr); return [], 1
    return created, 0


def identity(root: Path, website: Path, app: Path, website_port: int, app_port: int) -> str:
    """Return the visible startup identity for both local services."""
    return f"Runtime identity: repository={root}; website={website}; app={app}; website_port={website_port}; app_port={app_port}; commit={commit(root)}"
