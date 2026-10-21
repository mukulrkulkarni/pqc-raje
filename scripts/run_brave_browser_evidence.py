"""Run local Brave evidence checks for the server-rendered /app workflow.

Prerequisites on the user's machine:
  pip3 install playwright
  Start the local app, for example: python3 scripts/dev_local.py

This script does not download or install a browser. It uses the supplied Brave
executable and a temporary browser context. Screen-reader behavior is not
verified by this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BRAVE = "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
DEFAULT_CDP = "http://127.0.0.1:9222"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Brave local UX evidence checks")
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP)
    parser.add_argument("--output", default="out/browser-evidence-local")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    results: dict[str, object] = {"browser": BRAVE, "base_url": args.base_url}
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(args.cdp_url)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        context.set_offline(False)
        context.route("**/*", lambda route: route.abort() if not route.request.url.startswith(args.base_url) else route.continue_())
        page = context.new_page()

        page.goto(f"{args.base_url}/app/", wait_until="domcontentloaded")
        results["app_status"] = page.url
        results["app_has_script"] = page.locator("script").count() > 0
        results["app_has_stylesheet"] = page.locator('link[href*="style.css"]').count() > 0
        page.screenshot(path=str(out / "app-input.png"), full_page=True)

        # Keyboard evidence: collect focusable controls after repeated Tab presses.
        focus = []
        for _ in range(12):
            page.keyboard.press("Tab")
            focus.append(page.evaluate("document.activeElement && document.activeElement.outerHTML"))
        results["keyboard_focus_samples"] = focus

        # Reflow evidence at narrow viewport and enlarged page scale.
        page.set_viewport_size({"width": 320, "height": 900})
        results["narrow_scroll_width"] = page.evaluate("document.documentElement.scrollWidth")
        results["narrow_client_width"] = page.evaluate("document.documentElement.clientWidth")
        page.screenshot(path=str(out / "app-narrow.png"), full_page=True)

        page.set_viewport_size({"width": 1280, "height": 900})
        page.evaluate("document.body.style.zoom = '200%'")
        results["zoom_scroll_width"] = page.evaluate("document.documentElement.scrollWidth")
        page.screenshot(path=str(out / "app-zoom.png"), full_page=True)

        # Offline local navigation evidence. External requests are blocked by context.
        docs = context.new_page()
        try:
            docs.goto(f"{args.base_url}/docs/modules/index.html", wait_until="domcontentloaded")
            results["docs_offline_url"] = docs.url
            results["docs_offline_status"] = "loaded"
        except Exception as exc:  # evidence is recorded, not hidden
            results["docs_offline_status"] = f"failed: {exc}"

        (out / "browser-evidence.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        context.close()
        browser.close()

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
