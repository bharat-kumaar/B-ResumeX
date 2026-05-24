"""
Central configuration for B-ResumeX.
Override via environment variables in production.
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
    LOG_FOLDER = os.path.join(BASE_DIR, "logs")

    # Upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt"}

    # Database
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "b_resumex.db")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'b_resumex.db')}",
    )

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # AI engine
    AI_MODEL_PATH = os.path.join(BASE_DIR, "ai_engine", "models")
    AI_CONFIDENCE_THRESHOLD = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.75"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
