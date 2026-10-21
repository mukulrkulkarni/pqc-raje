"""Collect local Brave evidence after a verified CDP connection.

This tool never installs or downloads a browser.  Run ``--diagnose-cdp`` from
WSL first.  It reports the WSL-to-Windows endpoint state and optionally tests
Playwright's ``connect_over_cdp``.  It does not collect browser evidence during
diagnosis.  Screen-reader behavior is outside this tool's coverage.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

DEFAULT_PORT = 9222


def windows_host_address() -> str | None:
    """Return WSL's Windows gateway address without making a network request."""
    try:
        for line in Path("/etc/resolv.conf").read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[0] == "nameserver":
                socket.inet_aton(fields[1])
                return fields[1]
    except (OSError, UnicodeError, socket.error):
        return None
    return None


def cdp_version_url(cdp_url: str) -> str:
    return cdp_url.rstrip("/") + "/json/version"


def probe_cdp(cdp_url: str) -> tuple[bool, str]:
    """Probe CDP's documented local version endpoint with a short timeout."""
    try:
        with urlopen(cdp_version_url(cdp_url), timeout=3) as response:  # nosec B310: local user-selected CDP URL
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict) or "webSocketDebuggerUrl" not in payload:
            return False, "CDP_RESPONSE_INVALID: missing webSocketDebuggerUrl"
        return True, "CDP_HTTP_OK: " + str(payload.get("Browser", "browser identity unavailable"))
    except (URLError, OSError, ValueError, UnicodeError) as exc:
        return False, f"CDP_HTTP_FAILED: {exc}"


def diagnose_cdp(cdp_url: str, connect: bool) -> int:
    print(f"CDP_URL={cdp_url}")
    ok, message = probe_cdp(cdp_url)
    print(message)
    if not ok:
        print("DIAGNOSIS=WSL cannot reach CDP. Verify Windows localhost, listener address, then firewall.")
        return 2
    if not connect:
        print("DIAGNOSIS=HTTP endpoint is reachable; use --connect-check to test Playwright.")
        return 0
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("PLAYWRIGHT_UNAVAILABLE: install the project-approved Python dependency; do not install a browser.")
        return 3
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(cdp_url)
            print(f"PLAYWRIGHT_CDP_OK: contexts={len(browser.contexts)}")
            browser.close()
    except Exception as exc:  # Playwright exposes several transport-specific exception types.
        print(f"PLAYWRIGHT_CDP_FAILED: {exc}")
        print("DIAGNOSIS=CDP HTTP works but the WebSocket connection failed; retain this output for investigation.")
        return 4
    return 0


def collect_evidence(args: argparse.Namespace) -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("PLAYWRIGHT_UNAVAILABLE: install the project-approved Python dependency; no browser installation is required.")
        return 3

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    results: dict[str, object] = {"base_url": args.base_url, "cdp_url": args.cdp_url}
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(args.cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()
        page.goto(f"{args.base_url.rstrip('/')}/app/", wait_until="domcontentloaded")
        results["app_url"] = page.url
        results["app_has_script"] = page.locator("script").count() > 0
        results["app_has_stylesheet"] = page.locator('link[href*="style.css"]').count() > 0
        (out / "browser-evidence.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        context.close()
        browser.close()
    print(json.dumps(results, indent=2))
    return 0


def main() -> int:
    host = windows_host_address()
    default_cdp = f"http://{host}:{DEFAULT_PORT}" if host else f"http://127.0.0.1:{DEFAULT_PORT}"
    parser = argparse.ArgumentParser(description="Diagnose or collect local Brave CDP evidence")
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--cdp-url", default=default_cdp, help="CDP endpoint; WSL defaults to its Windows gateway")
    parser.add_argument("--output", default="out/browser-evidence-local")
    parser.add_argument("--diagnose-cdp", action="store_true", help="probe /json/version only; collect no evidence")
    parser.add_argument("--connect-check", action="store_true", help="with --diagnose-cdp, test Playwright connect_over_cdp")
    args = parser.parse_args()
    if args.connect_check and not args.diagnose_cdp:
        parser.error("--connect-check requires --diagnose-cdp")
    if args.diagnose_cdp:
        return diagnose_cdp(args.cdp_url, args.connect_check)
    return collect_evidence(args)


if __name__ == "__main__":
    raise SystemExit(main())
