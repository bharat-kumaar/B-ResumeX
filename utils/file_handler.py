"""Secure file upload and storage helpers."""

import os
import uuid
from werkzeug.utils import secure_filename


def save_upload(file, upload_folder: str) -> str:
    """Save uploaded file with a unique name; return absolute path."""
    os.makedirs(upload_folder, exist_ok=True)
    original = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{original}"
    path = os.path.join(upload_folder, unique_name)
    file.save(path)
    return os.path.abspath(path)
