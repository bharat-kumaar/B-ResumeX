"""Database initialization and schema migration."""

from flask import Flask
from sqlalchemy import inspect, text

from database.models import db


def init_db(app: Flask) -> None:
    db.init_app(app)
    with app.app_context():
        _ensure_schema()
        db.create_all()
        _migrate_columns()


def _ensure_schema() -> None:
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if "analysis_records" not in tables:
        return

    columns = {c["name"] for c in inspector.get_columns("analysis_records")}
    legacy = "file_path" in columns and "resume_id" not in columns
    missing_resumes = "resumes" not in tables

    if legacy or missing_resumes:
        db.drop_all()
        db.create_all()


def _migrate_columns() -> None:
    """Add rebuilt_json column if missing (SQLite ALTER)."""
    inspector = inspect(db.engine)
    if "analysis_records" not in inspector.get_table_names():
        return
    columns = {c["name"] for c in inspector.get_columns("analysis_records")}
    if "rebuilt_json" not in columns:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE analysis_records ADD COLUMN rebuilt_json TEXT"))
            conn.commit()
