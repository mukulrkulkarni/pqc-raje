"""Create and stop the local companion servers."""
from __future__ import annotations

import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import BaseServer

HOST = "127.0.0.1"


def website_server(root: Path, port: int) -> ThreadingHTTPServer:
    """Create a threaded server rooted at the generated website directory."""
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs)
    return ThreadingHTTPServer((HOST, port), handler)


def app_server(root: Path, port: int) -> BaseServer:
    """Create the Flask development server without its reloader."""
    if str(root) not in sys.path: sys.path.insert(0, str(root))
    from app import create_app
    from werkzeug.serving import make_server
    return make_server(HOST, port, create_app({"TESTING": False}), threaded=True)


def close(server: object) -> None:
    """Stop and close a server, even if shutdown raises."""
    try: server.shutdown()
    finally: server.server_close()
