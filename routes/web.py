"""Web UI routes."""

from flask import Blueprint, render_template, abort

from services.resume_service import ResumeService

web_bp = Blueprint("web", __name__)
resume_service = ResumeService()


@web_bp.route("/")
def index():
    return render_template("index.html")


@web_bp.route("/analyze")
def analyze():
    return render_template("analyze.html")


@web_bp.route("/dashboard")
@web_bp.route("/dashboard/<analysis_id>")
def dashboard(analysis_id=None):
    return render_template("dashboard.html", analysis_id=analysis_id)


@web_bp.route("/reports")
def reports():
    return render_template("reports.html")
