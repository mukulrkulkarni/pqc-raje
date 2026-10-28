"""Launcher integration tests using only temporary loopback services."""
from __future__ import annotations
import os
import signal
import socket
import subprocess
import sys
from pathlib import Path
from tests.launcher_test_support import distinct_ports, wait_for
ROOT = Path(__file__).parent.parent

def test_launcher_starts_identity_health_and_stops_without_orphans() -> None:
    website_port, app_port = distinct_ports(); env = os.environ | {"WEBSITE_PORT": str(website_port), "APP_PORT": str(app_port)}
    process = subprocess.Popen([sys.executable, "scripts/dev_local.py"], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    try:
        startup = [process.stdout.readline().strip() for _ in range(4)]; assert process.poll() is None, process.stderr.read()
        wait_for(f"http://127.0.0.1:{website_port}/"); wait_for(f"http://127.0.0.1:{app_port}/app/")
        process.send_signal(getattr(signal, "CTRL_BREAK_EVENT", signal.SIGINT)); remainder, stderr = process.communicate(timeout=5); stdout = "\n".join([*startup, remainder])
    finally:
        if process.poll() is None: process.kill(); process.communicate()
    assert process.returncode == 0, stderr
    assert "Runtime identity: repository=" in stdout and "commit=" in stdout
    assert f"Website: http://127.0.0.1:{website_port}/" in stdout and f"App:     http://127.0.0.1:{app_port}/app/" in stdout
    for port in (website_port, app_port):
        with socket.socket() as sock: assert sock.connect_ex(("127.0.0.1", port)) != 0
