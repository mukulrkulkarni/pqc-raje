"""Flask application factory for ELECTRE III web interface."""
from flask import Flask

SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'none'; base-uri 'none'; form-action 'self'; "
        "frame-ancestors 'none'; img-src 'self' data:; font-src 'self'; "
        "script-src 'unsafe-inline'; style-src 'unsafe-inline';",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = "uploads"
    if config:
        app.config.update(config)

    @app.after_request
    def add_security_headers(response):
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response

    from .routes import compute, preview, docs
    app.register_blueprint(docs.bp)
    app.register_blueprint(compute.bp)
    app.register_blueprint(preview.bp)
    return app
