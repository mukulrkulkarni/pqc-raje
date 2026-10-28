"""Flask application factory for ELECTRE III web interface."""
from datetime import timedelta
import os
from urllib.parse import urlsplit

from flask import Flask, request

# Base security headers applied to all responses
BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}

# Route-scoped CSP policies
CSP_DOCS = (
    "default-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; "
    "script-src 'self'; style-src 'unsafe-inline';"
)

CSP_APP = (
    "default-src 'none'; base-uri 'none'; form-action 'self'; "
    "frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; "
    "style-src 'self' 'unsafe-inline';"
)


def _companion_website_url(value: str) -> str:
    """Validate the local static-site base URL used by Flask documentation."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("COMPANION_WEBSITE_URL must be an absolute origin URL")
    return value.rstrip("/")


def _is_docs_route(path: str) -> bool:
    """Check if path is a documentation route (allows external JS)."""
    return path == "/" or path.startswith("/docs/")


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["COMPANION_WEBSITE_URL"] = os.environ.get(
        "COMPANION_WEBSITE_URL", "http://127.0.0.1:8000"
    )
    # Signed session metadata has the approved 30-minute lifetime.
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    if config:
        app.config.update(config)
    app.config["COMPANION_WEBSITE_URL"] = _companion_website_url(
        app.config["COMPANION_WEBSITE_URL"]
    )

    @app.after_request
    def add_security_headers(response):
        for header, value in BASE_HEADERS.items():
            response.headers[header] = value
        csp = CSP_DOCS if _is_docs_route(request.path) else CSP_APP
        response.headers["Content-Security-Policy"] = csp
        return response

    from .routes import compute, preview, docs, workflow
    app.register_blueprint(docs.bp)
    app.register_blueprint(workflow.bp)
    app.register_blueprint(compute.bp)
    app.register_blueprint(preview.bp)
    return app
