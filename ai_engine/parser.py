"""Extract structured text and sections from resume files."""

import os
from typing import Any


class ResumeParser:
    """Parse PDF, DOCX, and plain-text resumes into raw content."""

    SUPPORTED = {".pdf", ".docx", ".doc", ".txt"}

    def parse(self, filepath: str) -> dict[str, Any]:
        """Return normalized document payload from file path."""
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".txt":
            text = self._read_text(filepath)
        elif ext == ".pdf":
            text = self._read_pdf(filepath)
        elif ext in (".docx", ".doc"):
            text = self._read_docx(filepath)
        else:
            raise ValueError(f"Unsupported format: {ext}")

        return {
            "raw_text": text,
            "word_count": len(text.split()),
            "format": ext.lstrip("."),
        }

    def _read_text(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_pdf(self, filepath: str) -> str:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return self._read_text(filepath)

        reader = PdfReader(filepath)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    def _read_docx(self, filepath: str) -> str:
        try:
            from docx import Document
        except ImportError:
            return self._read_text(filepath)

        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
