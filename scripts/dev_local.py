"""Single-entry local dev runner: website + Flask app.

Starts:
- Static companion website (website/) at http://localhost:8000/
- Flask app at http://localhost:5000/

Why:
- Root-absolute links in the website require HTTP, not file://.
- Local UX is best when the website can link to a running app.

Usage:
  python scripts/dev_local.py

Config via environment variables:
- WEBSITE_PORT (default 8000)
- APP_PORT (default 5000)

Notes:
- Flask debug reloader is disabled to avoid double-start when threaded.
"""

from __future__ import annotations

import os
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = ROOT / "website"


class WebsiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBSITE_DIR), **kwargs)


def run_website(port: int) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), WebsiteHandler)
    print(f"[website] serving {WEBSITE_DIR} at http://localhost:{port}/")
    server.serve_forever()


def run_app(port: int) -> None:
    from app import create_app

    app = create_app({"TESTING": False})
    print(f"[app] starting Flask at http://localhost:{port}/")
    # debug=False and use_reloader=False avoid spawning extra processes.
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main() -> int:
    website_port = int(os.environ.get("WEBSITE_PORT", "8000"))
    app_port = int(os.environ.get("APP_PORT", "5000"))

    t = threading.Thread(target=run_website, args=(website_port,), daemon=True)
    t.start()

    # Run Flask in main thread so Ctrl+C works predictably.
    run_app(app_port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
