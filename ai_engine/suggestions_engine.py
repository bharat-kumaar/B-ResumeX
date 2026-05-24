"""Intelligent recommendation engine with contextual analysis."""

from typing import Any


class SuggestionsEngine:
    def generate(
        self,
        parsed: dict[str, Any],
        skills: dict[str, Any],
        ats: dict[str, Any],
        text: str,
    ) -> list[dict[str, str]]:
        suggestions = []
        missing = parsed.get("missing_sections", [])
        breakdown = ats.get("breakdown", {})
        contact = parsed.get("contact", {})
        weaknesses = ats.get("weaknesses", [])

        for sec in missing:
            suggestions.append({
                "type": "section",
                "priority": "high",
                "title": f"Add {sec.title()} section",
                "detail": self._section_tip(sec),
                "impact": "ATS completeness +15–25%",
            })

        if not contact.get("email"):
            suggestions.append({
                "type": "contact",
                "priority": "high",
                "title": "Add professional email",
                "detail": "Recruiters filter candidates without visible contact info in the header.",
                "impact": "Contact score critical",
            })

        if breakdown.get("keywords", 100) < 60:
            missing_kw = skills.get("missing_recommended", [])[:5]
            suggestions.append({
                "type": "keywords",
                "priority": "high",
                "title": "Optimize for job-description keywords",
                "detail": "Integrate role-specific terms: " + (", ".join(missing_kw) or "skills from posting") + ".",
                "impact": "Keyword score +10–20%",
            })

        if breakdown.get("readability", 100) < 60:
            suggestions.append({
                "type": "readability",
                "priority": "medium",
                "title": "Improve readability",
                "detail": "Use shorter sentences, bullet points, and consistent section headers.",
                "impact": "Recruiter scan time −30%",
            })

        for edu in parsed.get("education", [])[:1]:
            if not edu.get("degree") or not edu.get("institution"):
                suggestions.append({
                    "type": "education",
                    "priority": "high",
                    "title": "Clarify education entries",
                    "detail": "Format: Degree, Institution, Graduation Year (e.g. B.S. Computer Science, MIT, 2022).",
                    "impact": "Parsing accuracy",
                })

        for exp in parsed.get("experience", [])[:2]:
            for bullet in (exp.get("bullets") or [])[:2]:
                if len(bullet) < 50:
                    suggestions.append({
                        "type": "content",
                        "priority": "medium",
                        "title": "Strengthen experience bullet",
                        "detail": f"Expand with metrics and tools: '{bullet[:40]}…'",
                        "impact": "Impact narrative",
                    })
                    break

        if skills.get("skill_match_percent", 0) < 55:
            suggestions.append({
                "type": "skills",
                "priority": "medium",
                "title": "Increase skill match",
                "detail": f"Current match {skills.get('skill_match_percent', 0)}% — align skills section with target role.",
                "impact": "Interview shortlist rate",
            })

        for w in weaknesses[:2]:
            suggestions.append({
                "type": "ats",
                "priority": "medium",
                "title": "Address ATS weakness",
                "detail": w,
                "impact": "Overall ATS score",
            })

        if not suggestions:
            suggestions.append({
                "type": "general",
                "priority": "low",
                "title": "Tailor per application",
                "detail": "Use the rebuilt resume and customize summary keywords per job posting.",
                "impact": "Conversion",
            })

        order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: order.get(x["priority"], 3))
        return suggestions[:12]

    def _section_tip(self, sec: str) -> str:
        tips = {
            "summary": "Write 3–4 lines highlighting years of experience, domain, and top skills.",
            "skills": "Group technical and soft skills; mirror JD keywords.",
            "experience": "List roles reverse-chronologically with 3–5 quantified bullets each.",
            "education": "Degree, school, year, honors/GPA if strong.",
        }
        return tips.get(sec, f"Add a clearly labeled {sec} section with standard headers.")
