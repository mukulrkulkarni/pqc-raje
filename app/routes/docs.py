"""Documentation serving routes with path traversal protection."""
from flask import Blueprint, send_file, abort, render_template_string, make_response
from pathlib import Path
import re

bp = Blueprint("docs", __name__)

ALLOWED_MODULE_DOCS = {"config", "concordance", "discordance", "credibility",
                       "accumulator", "block", "ranking", "validate", "data"}
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

# Route-scoped CSP for tutorial pages (allows external JS file)
TUTORIAL_CSP = (
    "default-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; "
    "script-src 'self'; style-src 'unsafe-inline';"
)

def _validate_doc_name(name: str) -> bool:
    return bool(re.match(r"^[a-z_]+$", name)) and name in ALLOWED_MODULE_DOCS

def _serve_with_tutorial_csp(file_path: Path):
    """Serve file with tutorial-specific CSP (script-src 'self')."""
    if not file_path.exists():
        abort(404)
    response = make_response(send_file(file_path, mimetype="text/html"))
    response.headers["Content-Security-Policy"] = TUTORIAL_CSP
    return response

@bp.route("/")
def landing():
    gs_path = DOCS_DIR / "GETTING_STARTED.html"
    if not gs_path.exists():
        abort(404)
    return send_file(gs_path, mimetype="text/html")

@bp.route("/app")
def app_ui():
    return render_template_string('''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">
<title>ELECTRE III App</title>
<style>body{font-family:Arial,sans-serif;max-width:600px;margin:50px auto;text-align:center;}</style>
</head><body><h1>ELECTRE III Ranking</h1><p>Upload a matrix to begin.</p>
<p><a href="/">Back to docs</a></p></body></html>''')

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
    """Serve module tutorial with theme toggle (script-src 'self' CSP)."""
    if not _validate_doc_name(name):
        abort(404)
    tutorial_path = DOCS_DIR / "modules" / f"{name}_tutorial_side_by_side.html"
    return _serve_with_tutorial_csp(tutorial_path)
