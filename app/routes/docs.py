"""Documentation serving routes with path traversal protection."""
from flask import Blueprint, send_file, abort, render_template_string
from pathlib import Path
import re

bp = Blueprint("docs", __name__)

# Safe allow-list of servable doc files (no path components allowed)
ALLOWED_MODULE_DOCS = {"config", "concordance", "discordance", "credibility",
                       "accumulator", "block", "ranking", "validate", "data"}
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

def _validate_doc_name(name: str) -> bool:
    """Validate doc name against allow-list. Prevents path traversal."""
    return bool(re.match(r"^[a-z_]+$", name)) and name in ALLOWED_MODULE_DOCS

@bp.route("/")
def landing():
    """Serve Getting Started as landing page."""
    gs_path = DOCS_DIR / "GETTING_STARTED.html"
    if not gs_path.exists():
        abort(404)
    return send_file(gs_path, mimetype="text/html")

@bp.route("/app")
def app_ui():
    """Redirect to ranking UI (preview upload flow)."""
    return render_template_string('''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
<title>ELECTRE III App</title>
<style>body{font-family:Arial,sans-serif;max-width:600px;margin:50px auto;text-align:center;}</style>
</head><body><h1>ELECTRE III Ranking</h1><p>Upload a matrix to begin.</p>
<p><a href="/">Back to docs</a></p></body></html>''')

@bp.route("/docs/modules/<name>")
def module_doc(name: str):
    """Serve module documentation HTML."""
    if not _validate_doc_name(name):
        abort(404)
    doc_path = DOCS_DIR / "modules" / f"{name}.html"
    if not doc_path.exists():
        abort(404)
    return send_file(doc_path, mimetype="text/html")
