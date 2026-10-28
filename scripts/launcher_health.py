"""Check that launcher services serve their intended roots."""
from __future__ import annotations

from typing import Callable
from urllib.error import URLError
from urllib.request import urlopen

PAGES = ("/index.html", "/examples/index.html", "/modules/index.html", "/reference/index.html")


def health_errors(website_port: int, app_port: int, fetch: Callable = urlopen) -> list[str]:
    """Return failed endpoint diagnostics after both servers have started."""
    urls = [f"http://127.0.0.1:{website_port}{page}" for page in PAGES]
    urls.append(f"http://127.0.0.1:{app_port}/app/")
    errors = []
    for url in urls:
        try:
            with fetch(url, timeout=2) as response:
                if response.status != 200:
                    errors.append(f"health check failed: {url} returned {response.status}")
        except (OSError, URLError) as exc:
            errors.append(f"health check failed: {url}: {exc}")
    return errors
