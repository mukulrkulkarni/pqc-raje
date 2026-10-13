"""Flask application factory for ELECTRE III web interface."""

from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)

    # Default configuration
    app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB
    app.config["UPLOAD_FOLDER"] = "uploads"

    if config:
        app.config.update(config)

    # Register blueprints
    from .routes import compute, preview
    app.register_blueprint(compute.bp)
    app.register_blueprint(preview.bp)

    return app
