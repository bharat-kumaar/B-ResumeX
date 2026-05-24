"""Input validation helpers."""

import os

from werkzeug.datastructures import FileStorage


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def validate_resume_file(file: FileStorage, max_mb: int = 16) -> str | None:
    """Return error message or None if valid."""
    if not file.filename:
        return "Missing filename"

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pdf", "doc", "docx", "txt"}:
        return "Only PDF and DOCX/DOC/TXT files are supported."

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size == 0:
        return "File is empty."

    if size > max_mb * 1024 * 1024:
        return f"File exceeds {max_mb} MB limit."

    return None


def is_non_empty_string(value: str, min_len: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= min_len
