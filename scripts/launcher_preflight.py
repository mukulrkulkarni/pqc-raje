"""Validate local launcher inputs before starting services."""
from __future__ import annotations

import os
import socket
import subprocess
from pathlib import Path

HOST = "127.0.0.1"
REQUIRED_PAGES = ("index.html", "examples/index.html", "modules/index.html", "reference/index.html")


def port_owner(port: int) -> str:
    """Return the listener PID, or ``unknown`` when the platform cannot reveal it."""
    if os.name == "nt":
        command = ["netstat", "-ano", "-p", "tcp"]
        needle = f":{port}"
        output = subprocess.run(command, capture_output=True, text=True, check=False).stdout
        for line in output.splitlines():
            fields = line.split()
            if len(fields) >= 5 and needle in fields[1] and fields[3].upper() == "LISTENING":
                return fields[-1]
    else:
        command = ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"]
        output = subprocess.run(command, capture_output=True, text=True, check=False).stdout.strip()
        if output:
            return output.splitlines()[0]
    return "unknown"


def occupied_port(port: int) -> str | None:
    """Return an owning PID when the loopback port is already occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.2)
        if probe.connect_ex((HOST, port)) == 0:
            return port_owner(port)
    return None


def root_errors(website: Path, app: Path) -> list[str]:
    """Return deterministic diagnostics for stale or incorrect serving roots."""
    missing = [str(website / page) for page in REQUIRED_PAGES if not (website / page).is_file()]
    if not (app / "__init__.py").is_file():
        missing.append(str(app / "__init__.py"))
    return [f"missing required path: {path}" for path in missing]
