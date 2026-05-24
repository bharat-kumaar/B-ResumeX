"""General-purpose helper functions."""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def truncate(text: str, max_len: int = 120, suffix: str = "…") -> str:
    """Truncate long strings for UI previews."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix
