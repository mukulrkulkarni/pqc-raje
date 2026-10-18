"""Documentation serving routes with path traversal protection."""
from flask import Blueprint, send_file, abort, render_template_string
from pathlib import Path
import re

bp = Blueprint("docs", __name__)

ALLOWED_MODULE_DOCS = {"config", "concordance", "discordance", "credibility",
                       "accumulator", "block", "ranking", "validate", "data"}
ALLOWED_TUTORIAL_ASSETS = {"theme.js", "highlight.js"}
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"


def _validate_doc_name(name: str) -> bool:
    return bool(re.match(r"^[a-z_]+$", name)) and name in ALLOWED_MODULE_DOCS


def _validate_asset_name(asset: str) -> bool:
    """Validate asset name against strict allow-list."""
    return asset in ALLOWED_TUTORIAL_ASSETS


@bp.route("/")
def landing():
    gs_path = DOCS_DIR / "GETTING_STARTED.html"
    if not gs_path.exists():
        abort(404)
    return send_file(gs_path, mimetype="text/html")


@bp.route("/app")
def app_ui():
    # CSP is set via HTTP header in after_request (see app/__init__.py)
    return render_template_string('''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>ELECTRE III App</title>
<style>body{font-family:Arial,sans-serif;max-width:600px;margin:50px auto;text-align:center;}</style>
</head><body><h1>ELECTRE III Ranking</h1><p>Upload a matrix to begin.</p>
<p><a href="/">Back to docs</a></p></body></html>''')


@bp.route("/docs/modules")
def modules_index():
    """Serve a stable modules index page."""
    index_path = DOCS_DIR / "modules" / "index.html"
    if not index_path.exists():
        abort(404)
    return send_file(index_path, mimetype="text/html")


@bp.route("/docs/modules/<name>")
def module_doc(name: str):
    if not _validate_doc_name(name):
        abort(404)
    doc_path = DOCS_DIR / "modules" / f"{name}.html"
    if not doc_path.exists():
        abort(404)
    return send_file(doc_path, mimetype="text/html")


@bp.route("/docs/modules/<name>/tutorial")
def module_tutorial(name: str):
    """Serve module tutorial with theme toggle."""
    if not _validate_doc_name(name):
        abort(404)
    tutorial_path = DOCS_DIR / "modules" / f"{name}_tutorial_side_by_side.html"
    if not tutorial_path.exists():
        abort(404)
    return send_file(tutorial_path, mimetype="text/html")


@bp.route("/docs/modules/<name>/<target>_tutorial_side_by_side.html")
def linked_tutorial(name: str, target: str):
    """Resolve offline-compatible sibling links through the tutorial allow-list."""
    if not _validate_doc_name(name):
        abort(404)
    return module_tutorial(target)


@bp.route("/docs/modules/<name>/assets/<asset>")
def tutorial_asset(name: str, asset: str):
    """Serve tutorial assets (theme.js only) with strict allow-list."""
    if not _validate_doc_name(name):
        abort(404)
    if not _validate_asset_name(asset):
        abort(404)
    asset_path = DOCS_DIR / "modules" / "assets" / asset
    if not asset_path.exists():
        abort(404)
    resolved = asset_path.resolve()
    assets_dir = (DOCS_DIR / "modules" / "assets").resolve()
    if not str(resolved).startswith(str(assets_dir)):
        abort(404)
    mimetype = "application/javascript" if asset.endswith(".js") else "application/octet-stream"
    return send_file(asset_path, mimetype=mimetype)
