"""Build the static companion website into the website/ folder.

Design goals:
- Pure static output (no server runtime required)
- Easy to switch domain targets and nav order via website/site-config.json
- Preserve offline-first docs/tutorial HTML (no external assets)

This script is intentionally small and deterministic.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
WEBSITE = ROOT / "website"

MODULES = [
    "config",
    "validate",
    "block",
    "accumulator",
    "ranking",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_config() -> dict:
    return json.loads(read_text(WEBSITE / "site-config.json"))


def apply_domains(html: str, docs_base: str, app_base: str) -> str:
    # Only replace our known placeholders/domains.
    html = html.replace("https://docs.pqcmig.scoring.draft", docs_base.rstrip("/"))
    html = html.replace("https://app.pqcmig.scoring.draft", app_base.rstrip("/"))
    return html


def normalize_tutorial_assets(html: str) -> str:
    # Tutorials copied under /modules/<name>/tutorial/index.html need ../assets/
    html = html.replace('src="assets/theme.js"', 'src="../assets/theme.js"')
    html = html.replace('src="assets/highlight.js"', 'src="../assets/highlight.js"')
    # Some tutorials already use ../assets; keep stable.
    return html


def inject_primary_nav(html: str, active_href: str) -> str:
    """Inject a simple primary nav after <body>.

    Requirements (user):
    - Must provide a way back to Getting Started from tutorial pages.
    - Must include both local website and Flask home links.

    Design choice:
    - Keep this nav *non-sticky* to avoid overlapping the tutorial's own sticky
      sidebar and sticky topbar.
    """
    if not re.search(r"<body(?:\s|>)", html, flags=re.IGNORECASE):
        raise ValueError('Tutorial HTML missing <body> tag')

    nav = (
        '<nav aria-label="Primary" style="background:var(--bg,#fff);'
        'border-bottom:1px solid var(--border,#e2e8f0);'
        'padding:10px 16px;font-family:var(--sans,system-ui);font-size:13px;">'
        '<a href="/index.html" style="margin-right:12px;text-decoration:none;">Getting Started</a>'
        '<a href="/app/index.html" style="margin-right:12px;text-decoration:none;">App</a>'
        '<a href="/modules/index.html" style="margin-right:12px;text-decoration:none;">Tutorials</a>'
        '<span style="color:var(--text-dim,#64748b);margin:0 8px;">|</span>'
        '<a href="http://localhost:5000/" style="margin-right:12px;text-decoration:none;">Flask home</a>'
        '<a href="http://localhost:5000/docs/modules" style="text-decoration:none;">Flask modules</a>'
        '</nav>'
    )

    if 'aria-label="Primary"' in html:
        # Ensure required Flask back-links are present even if a nav exists.
        if 'http://localhost:5000/' in html and 'http://localhost:5000/docs/modules' in html:
            return html
        # If an existing nav is present but lacks required links, fail fast.
        raise ValueError('Tutorial HTML has Primary nav but lacks required links')

    # Inject after the first real <body ...> tag.
    new_html, n = re.subn(r"(<body(?:\s|>)[^>]*>)", r"\1\n" + nav, html, count=1, flags=re.IGNORECASE)
    if n != 1:
        raise ValueError(f"Expected exactly one <body> injection, got {n}")
    return new_html


def copy_assets() -> None:
    # Copy shared assets used by tutorials.
    for asset in ["theme.js", "highlight.js"]:
        src = DOCS / "modules" / "assets" / asset
        dst = WEBSITE / "modules" / "assets" / asset
        write_text(dst, read_text(src))


def build_module(name: str, cfg: dict) -> None:
    docs_base = cfg["docsBaseUrl"]
    app_base = cfg["appBaseUrl"]

    # Module landing
    # Prefer website-written landing if exists, else generate.
    landing_path = WEBSITE / "modules" / name / "index.html"
    if not landing_path.exists():
        landing = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; script-src 'self'; style-src 'unsafe-inline';\">
<title>{name}</title>
<body>
<nav aria-label=\"Primary\"><a href=\"/index.html\">Getting Started</a><a href=\"/app/index.html\">App</a><a href=\"/modules/index.html\">Tutorials</a></nav>
<main>
<h1>{name}</h1>
<p><a href=\"/modules/{name}/tutorial/\">Open tutorial</a></p>
<p><a href=\"{docs_base}/docs/modules/{name}\">Open Flask-served module doc</a></p>
</main>
</body></html>
"""
        write_text(landing_path, landing)
    else:
        landing = apply_domains(read_text(landing_path), docs_base, app_base)
        write_text(landing_path, landing)

    # Tutorial
    src_tut = DOCS / "modules" / f"{name}_tutorial_side_by_side.html"
    if not src_tut.exists():
        return
    tut = read_text(src_tut)
    tut = normalize_tutorial_assets(tut)
    tut = apply_domains(tut, docs_base, app_base)
    tut = inject_primary_nav(tut, active_href=f"/modules/{name}/tutorial/")
    dst_tut = WEBSITE / "modules" / name / "tutorial" / "index.html"
    write_text(dst_tut, tut)


def main() -> int:
    cfg = load_config()
    copy_assets()

    # Ensure index/app/modules index have consistent nav and updated domains.
    index = apply_domains(read_text(WEBSITE / "index.html"), cfg["docsBaseUrl"], cfg["appBaseUrl"])
    write_text(WEBSITE / "index.html", index)

    app_index = apply_domains(read_text(WEBSITE / "app" / "index.html"), cfg["docsBaseUrl"], cfg["appBaseUrl"])
    write_text(WEBSITE / "app" / "index.html", app_index)

    mod_index = apply_domains(read_text(WEBSITE / "modules" / "index.html"), cfg["docsBaseUrl"], cfg["appBaseUrl"])
    write_text(WEBSITE / "modules" / "index.html", mod_index)

    for name in MODULES:
        build_module(name, cfg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
