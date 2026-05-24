"""Deep resume intelligence — comprehensive analysis report."""

from typing import Any


class InsightsEngine:
    def analyze(
        self,
        parsed: dict,
        skills: dict,
        ats: dict,
        keywords: dict,
    ) -> dict[str, Any]:
        contact = parsed.get("contact", {})
        metrics = parsed.get("metrics", {})
        missing = parsed.get("missing_sections", [])

        quality = self._quality_score(parsed, skills, ats, contact)
        gaps = self._content_gaps(parsed, skills, missing)
        highlights = self._highlights(parsed, skills, ats)

        return {
            "quality_score": quality,
            "quality_label": self._quality_label(quality),
            "strengths": ats.get("strengths", []) + highlights.get("strengths", []),
            "weaknesses": ats.get("weaknesses", []) + gaps,
            "missing_sections": missing,
            "section_status": parsed.get("section_status", {}),
            "highlights": highlights,
            "content_gaps": gaps,
            "keyword_analysis": {
                "top_keywords": keywords.get("top_keywords", [])[:10],
                "action_verbs": keywords.get("action_verbs_used", []),
                "density": keywords.get("keyword_density", 0),
            },
            "contact_completeness": self._contact_score(contact),
            "experience_depth": self._exp_depth(parsed.get("experience", [])),
            "education_quality": self._edu_quality(parsed.get("education", [])),
        }

    def _quality_score(self, parsed, skills, ats, contact) -> int:
        score = ats.get("overall", 0) * 0.5
        score += min(20, skills.get("total_count", 0) * 2)
        score += 10 if contact.get("name") and contact.get("email") else 0
        score += 5 * len(parsed.get("experience", []))
        score += 5 if parsed.get("education") else 0
        return min(100, int(score))

    def _quality_label(self, q: int) -> str:
        if q >= 85:
            return "Excellent"
        if q >= 70:
            return "Strong"
        if q >= 55:
            return "Good"
        return "Needs Improvement"

    def _content_gaps(self, parsed, skills, missing) -> list[str]:
        gaps = [f"Missing {s} section" for s in missing]
        if not parsed.get("achievements") and not any(
            "%" in (e.get("detail") or "") for e in parsed.get("experience", [])
        ):
            gaps.append("No quantified achievements detected")
        if skills.get("skill_match_percent", 0) < 50:
            gaps.append(f"Low role skill match ({skills.get('skill_match_percent', 0)}%)")
        if not parsed.get("summary"):
            gaps.append("No professional summary")
        return gaps[:8]

    def _highlights(self, parsed, skills, ats) -> dict:
        h = {"strengths": [], "notable": []}
        if ats.get("overall", 0) >= 80:
            h["strengths"].append("Strong overall ATS compatibility")
        if skills.get("total_count", 0) >= 10:
            h["strengths"].append(f"{skills['total_count']} skills identified")
        if parsed.get("contact", {}).get("linkedin"):
            h["notable"].append("LinkedIn profile present")
        for ed in parsed.get("education", [])[:1]:
            if ed.get("gpa"):
                h["notable"].append(f"GPA listed: {ed['gpa']}")
        return h

    def _contact_score(self, contact: dict) -> int:
        fields = ["name", "email", "phone", "linkedin"]
        return int(sum(25 for f in fields if contact.get(f)))

    def _exp_depth(self, experience: list) -> dict:
        bullets = sum(len(e.get("bullets", [])) for e in experience)
        with_metrics = sum(
            1 for e in experience
            for b in e.get("bullets", [])
            if any(c.isdigit() for c in b)
        )
        return {
            "roles": len(experience),
            "total_bullets": bullets,
            "quantified_bullets": with_metrics,
            "depth_score": min(100, bullets * 8 + with_metrics * 15),
        }

    def _edu_quality(self, education: list) -> dict:
        complete = sum(
            1 for e in education
            if e.get("degree") and e.get("institution") and e.get("years")
        )
        return {
            "entries": len(education),
            "complete_entries": complete,
            "score": min(100, complete * 40 + len(education) * 20),
        }
