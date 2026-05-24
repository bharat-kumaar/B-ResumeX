"""spaCy loader with graceful fallback."""

from __future__ import annotations

_nlp = None
_nlp_mode = "none"


def get_nlp():
    """Return loaded spaCy model or None."""
    global _nlp, _nlp_mode
    if _nlp is not None or _nlp_mode == "failed":
        return _nlp

    try:
        import spacy
        for model in ("en_core_web_sm", "en_core_web_md"):
            try:
                _nlp = spacy.load(model)
                _nlp_mode = model
                return _nlp
            except OSError:
                continue
        _nlp = spacy.blank("en")
        if "sentencizer" not in _nlp.pipe_names:
            _nlp.add_pipe("sentencizer")
        _nlp_mode = "blank"
        return _nlp
    except Exception:
        _nlp_mode = "failed"
        _nlp = None
        return None


def nlp_mode() -> str:
    get_nlp()
    return _nlp_mode
