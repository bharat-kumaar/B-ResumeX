"""Clean raw resume text from PDF/DOCX extraction noise."""

import re


# Common unicode / OCR artifacts we want to normalize early.
_OCR_FIXES = {
    "\u00a0": " ",  # non-breaking space
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2212": "-",  # minus sign
    "\u2022": "•",  # bullet
    "\u25cf": "•",  # black circle
    "\u00b7": "•",  # middle dot
}


def normalize(text: str) -> str:
    """Return cleaned text with improved section-splitting stability."""

    if text is None:
        return ""

    for k, v in _OCR_FIXES.items():
        text = text.replace(k, v)

    # Canonicalize newlines first.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove form feed artifacts.
    text = re.sub(r"\f", "\n", text)

    # Fix hyphenation across lines: "experi-\nence" -> "experience"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize spacing around newlines.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)

    # Collapse excessive blank lines to at most 2 newlines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Ensure bullet lines do not get glued to previous sentences.
    # Turn "some sentence• bullet" into two lines.
    text = re.sub(r"(\S)\s*•\s*(\S)", r"\1\n• \2", text)

    return text.strip()

