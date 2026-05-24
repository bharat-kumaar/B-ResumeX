"""Full resume intelligence pipeline v3.1."""

from typing import Any

from ai_engine.parsing.advanced_parser import AdvancedResumeParser
from ai_engine.ats_engine import ATSEngine
from ai_engine.suggestions_engine import SuggestionsEngine
from ai_engine.resume_rebuilder import ResumeRebuilder
from ai_engine.insights_engine import InsightsEngine
from ai_engine.parsing.nlp_loader import nlp_mode


class ResumeAnalyzer:
    def __init__(self):
        self.parser = AdvancedResumeParser()
        self.ats = ATSEngine()
        self.suggestions = SuggestionsEngine()
        self.rebuilder = ResumeRebuilder()
        self.insights = InsightsEngine()

    def run(self, filepath: str) -> dict[str, Any]:
        parsed = self.parser.parse_file(filepath)
        text = parsed.get("document", {}).get("raw_text", "")
        skill_data = parsed.get("skills", {})
        keywords = parsed.get("keywords", {})

        ats_result = self.ats.score(text, parsed, skill_data)
        deep_insights = self.insights.analyze(parsed, skill_data, ats_result, keywords)
        suggestion_list = self.suggestions.generate(parsed, skill_data, ats_result, text)
        rebuilt = self.rebuilder.build(parsed, skill_data, ats_result, suggestion_list)

        return {
            "parsed": parsed,
            "skills": skill_data,
            "ats": ats_result,
            "suggestions": suggestion_list,
            "rebuilt_resume": rebuilt,
            "insights": deep_insights,
            "analytics": self._analytics(parsed, skill_data, ats_result, deep_insights),
            "engine": {
                "nlp_mode": nlp_mode(),
                "version": "3.1",
                "parse_confidence": parsed.get("metrics", {}).get("parse_confidence", 0),
            },
        }

    def _analytics(self, parsed: dict, skills: dict, ats: dict, insights: dict) -> dict[str, Any]:
        m = parsed.get("metrics", {})
        exp_d = insights.get("experience_depth", {})
        edu_q = insights.get("education_quality", {})
        return {
            "word_count": m.get("word_count", 0),
            "bullet_count": m.get("bullet_count", 0),
            "sections_count": len(parsed.get("sections_detected", [])),
            "skills_count": skills.get("total_count", 0),
            "skill_match_percent": skills.get("skill_match_percent", 0),
            "experience_entries": len(parsed.get("experience", [])),
            "education_entries": len(parsed.get("education", [])),
            "project_entries": len(parsed.get("projects", [])),
            "strength": ats.get("strength", "moderate"),
            "ats_score": ats.get("overall", 0),
            "readability": ats.get("readability", m.get("readability_score", 0)),
            "quality_score": insights.get("quality_score", 0),
            "quality_label": insights.get("quality_label", ""),
            "parse_confidence": m.get("parse_confidence", 0),
            "experience_depth_score": exp_d.get("depth_score", 0),
            "education_quality_score": edu_q.get("score", 0),
            "projected_ats_after_rebuild": round(
                min(98, ats.get("overall", 0) + 8 + (100 - ats.get("overall", 0)) * 0.1), 1
            ),
        }
