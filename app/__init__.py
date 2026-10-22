"""Flask application factory for ELECTRE III web interface."""
from datetime import timedelta

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


def _is_docs_route(path: str) -> bool:
    """Check if path is a documentation route (allows external JS)."""
    return path == "/" or path.startswith("/docs/")


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = "uploads"
    # Signed session metadata has the approved 30-minute lifetime.
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    if config:
        app.config.update(config)

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
