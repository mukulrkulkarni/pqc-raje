"""Serve the static companion website locally.

Why:
- The website uses root-absolute links like /modules/... which do not work with file:// URLs.
- A local HTTP server makes those links resolve correctly.

Usage:
  python scripts/serve_website.py
  # then open http://localhost:8000/

Options:
- Set PORT env var to override the port.
"""

from __future__ import annotations

import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = ROOT / "website"


class WebsiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEBSITE_DIR), **kwargs)


def main() -> int:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), WebsiteHandler)
    print(f"Serving website/ at http://localhost:{port}/")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
