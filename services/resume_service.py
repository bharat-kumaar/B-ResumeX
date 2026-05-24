"""Orchestrates upload, analysis, persistence, rebuild, and export."""

import json
import os
import uuid
from datetime import datetime, timezone

from flask import current_app, send_file
from werkzeug.datastructures import FileStorage

from ai_engine.analyzer import ResumeAnalyzer
from database.models import db, Resume, AnalysisRecord
from utils.file_handler import save_upload
from services.export_service import ExportService


class ResumeService:
    def __init__(self):
        self.analyzer = ResumeAnalyzer()
        self.exporter = ExportService()

    def analyze_upload(self, file: FileStorage) -> dict:
        resume_id = str(uuid.uuid4())
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        filepath = save_upload(file, upload_dir)

        resume = Resume(
            id=resume_id,
            original_filename=file.filename,
            stored_filename=os.path.basename(filepath),
            file_path=filepath,
            file_size=os.path.getsize(filepath),
            file_type=os.path.splitext(file.filename)[1].lower().lstrip("."),
        )
        db.session.add(resume)
        db.session.flush()
        return self._run_pipeline(resume, filepath)

    def _run_pipeline(self, resume: Resume, filepath: str) -> dict:
        analysis = self.analyzer.run(filepath)
        ats = analysis["ats"]
        rebuilt = analysis.get("rebuilt_resume", {})

        analysis_id = str(uuid.uuid4())
        payload = {
            "id": analysis_id,
            "resume_id": resume.id,
            "filename": resume.original_filename,
            "file_type": resume.file_type,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            **analysis,
            "scores": {
                "overall": ats["overall"],
                "breakdown": ats["breakdown"],
                "grade": ats["grade"],
            },
        }

        record = AnalysisRecord(
            id=analysis_id,
            resume_id=resume.id,
            ats_score=ats["overall"],
            grade=ats["grade"],
            result_json=json.dumps(payload),
            rebuilt_json=json.dumps(rebuilt),
        )
        db.session.add(record)
        db.session.commit()
        self._write_report(analysis_id, payload)
        return payload

    def get_analysis(self, analysis_id: str) -> dict | None:
        record = AnalysisRecord.query.filter_by(id=analysis_id).first()
        if not record:
            return None
        data = record.get_payload()
        edited = record.get_rebuilt_edited()
        if edited:
            data["rebuilt_resume"] = edited
        return data

    def save_rebuilt_resume(self, analysis_id: str, resume_doc: dict) -> dict | None:
        record = AnalysisRecord.query.filter_by(id=analysis_id).first()
        if not record:
            return None
        record.rebuilt_json = json.dumps(resume_doc)
        payload = record.get_payload()
        payload["rebuilt_resume"] = resume_doc
        record.result_json = json.dumps(payload)
        db.session.commit()
        return payload

    def export_file(self, analysis_id: str, fmt: str):
        record = AnalysisRecord.query.filter_by(id=analysis_id).first()
        if not record:
            return None, None
        doc = record.get_rebuilt_edited() or record.get_rebuilt()
        if not doc:
            return None, None

        base = os.path.splitext(record.resume.original_filename)[0] if record.resume else "resume"
        if fmt == "pdf":
            path = self.exporter.export_pdf(doc, f"{base}_optimized.pdf")
            return path, "application/pdf"
        path = self.exporter.export_docx(doc, f"{base}_optimized.docx")
        return path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def list_history(self, limit: int = 20) -> list[dict]:
        records = (
            AnalysisRecord.query.order_by(AnalysisRecord.created_at.desc())
            .limit(limit)
            .all()
        )
        return [r.to_summary() for r in records]

    def get_dashboard_stats(self) -> dict:
        total = AnalysisRecord.query.count()
        if total == 0:
            return {"total_analyses": 0, "avg_ats_score": 0, "recent": []}
        from sqlalchemy import func
        avg = db.session.query(func.avg(AnalysisRecord.ats_score)).scalar() or 0
        return {
            "total_analyses": total,
            "avg_ats_score": round(float(avg), 1),
            "recent": self.list_history(5),
        }

    def _write_report(self, analysis_id: str, payload: dict) -> None:
        reports_dir = current_app.config["REPORTS_FOLDER"]
        os.makedirs(reports_dir, exist_ok=True)
        with open(os.path.join(reports_dir, f"{analysis_id}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
