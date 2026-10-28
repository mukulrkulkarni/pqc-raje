"""Parse launcher environment configuration."""
from __future__ import annotations

import os
import sys


def port(name: str, default: int) -> int:
    """Read one validated TCP port from the environment."""
    raw = os.environ.get(name, str(default))
    try: value = int(raw)
    except ValueError as exc: raise ValueError(f"{name} must be an integer between 1 and 65535; got {raw!r}") from exc
    if not 1 <= value <= 65535: raise ValueError(f"{name} must be between 1 and 65535; got {value}")
    return value


def main(run: callable) -> int:
    """Run the launcher with its configured ports."""
    try: return run(port("WEBSITE_PORT", 8000), port("APP_PORT", 5000))
    except ValueError as exc: print(f"Configuration error: {exc}", file=sys.stderr); return 2
