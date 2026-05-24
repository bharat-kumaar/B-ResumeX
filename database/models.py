"""SQLAlchemy ORM models."""

import json
from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.String(36), primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    file_type = db.Column(db.String(16), nullable=False)
    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    analyses = db.relationship("AnalysisRecord", backref="resume", lazy=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.isoformat(),
        }


class AnalysisRecord(db.Model):
    __tablename__ = "analysis_records"

    id = db.Column(db.String(36), primary_key=True)
    resume_id = db.Column(db.String(36), db.ForeignKey("resumes.id"), nullable=False)
    ats_score = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(2), default="C")
    result_json = db.Column(db.Text, nullable=False)
    rebuilt_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def get_payload(self) -> dict:
        return json.loads(self.result_json)

    def get_rebuilt(self) -> dict | None:
        if self.rebuilt_json:
            return json.loads(self.rebuilt_json)
        data = self.get_payload()
        return data.get("rebuilt_resume")

    def get_rebuilt_edited(self) -> dict | None:
        return self.get_rebuilt()

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "ats_score": self.ats_score,
            "grade": self.grade,
            "created_at": self.created_at.isoformat(),
            "filename": self.resume.original_filename if self.resume else None,
        }
