"""
B-ResumeX — AI Resume Intelligence Platform
Production Flask application entry point.
"""

import os
from flask import Flask, render_template

from config import Config
from database.connection import init_db
from routes.web import web_bp
from routes.api import api_bp


def create_app(config_class=Config):
    """Application factory for scalable deployment."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure runtime directories exist
    for folder in (
        app.config["UPLOAD_FOLDER"],
        app.config["REPORTS_FOLDER"],
        app.config.get("LOG_FOLDER", "logs"),
    ):
        os.makedirs(folder, exist_ok=True)

    # Database
    init_db(app)

    # Blueprints
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    @app.context_processor
    def inject_globals():
        return {
            "app_name": "B-ResumeX",
            "app_tagline": "AI Resume Intelligence Platform",
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
