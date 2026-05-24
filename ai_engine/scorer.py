"""Legacy scorer — delegates to ATS engine for backward compatibility."""

from typing import Any

from ai_engine.ats_engine import ATSEngine


class ResumeScorer:
    """Backward-compatible wrapper around ATSEngine."""

    def __init__(self):
        self._ats = ATSEngine()

    def evaluate(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Map new analysis shape to legacy scores format."""
        ats = analysis.get("ats", {})
        if ats:
            return {
                "overall": ats.get("overall", 0),
                "breakdown": ats.get("breakdown", {}),
                "grade": ats.get("grade", "C"),
                "recommendations": [
                    s["detail"] for s in analysis.get("suggestions", [])[:5]
                ],
            }

        return self._ats.score(
            "",
            analysis.get("parsed", analysis),
            analysis.get("skills", {}),
        )
