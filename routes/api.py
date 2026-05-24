"""REST API v1 — resume intelligence endpoints."""

import os

from flask import Blueprint, jsonify, request, current_app, send_file

from utils.validators import allowed_file, validate_resume_file
from utils.file_handler import save_upload
from services.resume_service import ResumeService

api_bp = Blueprint("api", __name__)
# Lazy init to avoid loading AI models during health checks / imports.
resume_service = None


def get_resume_service():
    global resume_service
    if resume_service is None:
        resume_service = ResumeService()
    return resume_service



@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "operational",
        "service": "B-ResumeX",
        "version": "3.0.0",
    })


@api_bp.route("/upload", methods=["POST"])
def upload_resume():
    """Upload only — returns resume metadata (optional pre-step)."""
    error = _validate_upload()
    if error:
        return jsonify({"success": False, "error": error}), 400

    file = request.files["resume"]
    filepath = save_upload(file, current_app.config["UPLOAD_FOLDER"])
    return jsonify({
        "success": True,
        "data": {
            "path": filepath,
            "filename": file.filename,
        },
    })


@api_bp.route("/analyze", methods=["POST"])
def analyze_resume():
    """Upload and run full AI analysis pipeline."""
    error = _validate_upload()
    if error:
        return jsonify({"success": False, "error": error}), 400

    file = request.files["resume"]
    extra_error = validate_resume_file(file)
    if extra_error:
        return jsonify({"success": False, "error": extra_error}), 400

    try:
        result = get_resume_service().analyze_upload(file)

        return jsonify({"success": True, "data": result})
    except Exception as exc:
        current_app.logger.exception("Analysis failed")
        return jsonify({"success": False, "error": str(exc)}), 500


@api_bp.route("/analyses", methods=["GET"])
def list_analyses():
    """Analysis history for dashboard."""
    limit = min(int(request.args.get("limit", 20)), 50)
    return jsonify({
        "success": True,
        "data": get_resume_service().list_history(limit),
    })


@api_bp.route("/analyses/<analysis_id>", methods=["GET"])
def get_analysis(analysis_id):
    """Full analysis payload by ID."""
    data = resume_service.get_analysis(analysis_id)
    if not data:
        return jsonify({"success": False, "error": "Analysis not found"}), 404
    return jsonify({"success": True, "data": data})


@api_bp.route("/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    """Alias for analyses — backward compatible."""
    return get_analysis(report_id)


@api_bp.route("/dashboard/stats", methods=["GET"])
def dashboard_stats():
    return jsonify({
        "success": True,
        "data": resume_service.get_dashboard_stats(),
    })


@api_bp.route("/analyses/<analysis_id>/resume", methods=["PUT"])
def save_rebuilt_resume(analysis_id):
    body = request.get_json(silent=True)
    if not body or "rebuilt_resume" not in body:
        return jsonify({"success": False, "error": "rebuilt_resume JSON required"}), 400
    data = resume_service.save_rebuilt_resume(analysis_id, body["rebuilt_resume"])
    if not data:
        return jsonify({"success": False, "error": "Analysis not found"}), 404
    return jsonify({"success": True, "data": data})


@api_bp.route("/analyses/<analysis_id>/export/<fmt>", methods=["GET"])
def export_resume(analysis_id, fmt):
    if fmt not in ("pdf", "docx"):
        return jsonify({"success": False, "error": "Use pdf or docx"}), 400
    path, mime = resume_service.export_file(analysis_id, fmt)
    if not path:
        return jsonify({"success": False, "error": "Export failed"}), 404
    return send_file(path, as_attachment=True, download_name=path.split(os.sep)[-1], mimetype=mime)


def _validate_upload() -> str | None:
    if "resume" not in request.files:
        return "No resume file provided"
    file = request.files["resume"]
    if not file or file.filename == "":
        return "Empty filename"
    if not allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
        return "Unsupported file type. Use PDF, DOCX, DOC, or TXT."
    return None
