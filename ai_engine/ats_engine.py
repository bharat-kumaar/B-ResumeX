"""Advanced ATS scoring — formatting, keywords, completeness, structure, readability, contact."""

import re
from typing import Any


class ATSEngine:
    WEIGHTS = {
        "formatting": 0.16,
        "keywords": 0.22,
        "completeness": 0.24,
        "structure": 0.14,
        "readability": 0.12,
        "contact": 0.12,
    }

    REQUIRED = ["experience", "education", "skills", "summary"]

    def score(self, text: str, parsed: dict[str, Any], skills: dict[str, Any]) -> dict[str, Any]:
        metrics = parsed.get("metrics", {})
        missing = parsed.get("missing_sections", [])

        breakdown = {
            "formatting": self._formatting(text, parsed),
            "keywords": self._keywords(text, skills, parsed.get("keywords", {})),
            "completeness": self._completeness(parsed, missing),
            "structure": self._structure(parsed),
            "readability": metrics.get("readability_score", self._readability_fallback(text)),
            "contact": self._contact(parsed.get("contact", {}), metrics),
        }

        overall = round(sum(breakdown[k] * self.WEIGHTS[k] for k in self.WEIGHTS), 1)
        strengths, weaknesses = self._swot(breakdown, parsed, skills)

        return {
            "overall": overall,
            "breakdown": breakdown,
            "grade": self._grade(overall),
            "strength": self._strength(overall),
            "missing_sections": missing,
            "readability": breakdown["readability"],
            "keyword_optimization": breakdown["keywords"],
            "formatting_quality": breakdown["formatting"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "detailed_report": self._detailed_report(breakdown, missing),
        }

    def _formatting(self, text: str, parsed: dict) -> int:
        score = 55
        wc = parsed.get("metrics", {}).get("word_count", len(text.split()))
        if 300 <= wc <= 850:
            score += 22
        bullets = parsed.get("metrics", {}).get("bullet_count", 0)
        score += min(18, bullets * 3)
        if not re.search(r"[\x00-\x08]", text):
            score += 8
        if len(re.findall(r"\n{3,}", text)) > 3:
            score -= 8
        return max(0, min(100, score))

    def _keywords(self, text: str, skills: dict, kw: dict) -> int:
        """More stable keyword scoring.

        Uses:
        - extracted skills coverage
        - density (how many extracted skills show up)
        - action-verb coverage if present
        - light boosts for metrics (numbers)
        """

        lower = text.lower()
        extracted = {self._canon_skill(s) for s in (skills.get("all_skills") or [])}
        match_percent = float(skills.get("skill_match_percent", 0))

        action_verbs_used = (
            kw.get("action_verbs_used")
            or kw.get("action_verbs")
            or []
        )

        # density: how many extracted skills appear (approx)
        density_score = 0
        if extracted:
            hits = 0
            for s in extracted:
                if not s:
                    continue
                s_compact = s.replace(" ", "")
                t_compact = lower.replace(" ", "")

                # single token: use word boundaries
                if " " not in s:
                    if re.search(rf"(?<![a-z0-9]){re.escape(s)}(?![a-z0-9])", lower, re.IGNORECASE):
                        hits += 1
                else:
                    # multi-word: punctuation tolerant substring in compact forms
                    if s_compact in t_compact:
                        hits += 1

            density = hits / max(1, len(extracted))
            density_score = int(min(35, 10 + density * 35))

        score = 25
        score += min(35, (match_percent / 100.0) * 35)
        score += density_score
        score += min(20, len(action_verbs_used or []) * 2.5)

        if re.search(r"\d+%|\$\d|#\d", text):
            score += 12

        if not extracted and not kw:
            score -= 10

        if action_verbs_used:
            score += 8

        return max(0, min(100, int(score)))

    def _canon_skill(self, s: str) -> str:
        s = (s or "").strip().lower()
        s = s.replace("/", " ").replace("-", " ")
        s = re.sub(r"\s+", " ", s)
        return s

    def _completeness(self, parsed: dict, missing: list) -> int:
        score = 100 - len(missing) * 18
        if parsed.get("education"):
            score += 5
        if parsed.get("experience"):
            score += 5
        if parsed.get("projects"):
            score += 3
        return max(0, min(100, score))

    def _structure(self, parsed: dict) -> int:
        n = len(parsed.get("sections_detected", []))
        score = 40 + min(40, n * 9)
        if parsed.get("experience") and parsed.get("education"):
            score += 15
        return max(0, min(100, score))

    def _contact(self, contact: dict, metrics: dict) -> int:
        score = 0
        if contact.get("email") or metrics.get("has_email"):
            score += 40
        if contact.get("phone") or metrics.get("has_phone"):
            score += 35
        if contact.get("linkedin") or metrics.get("has_linkedin"):
            score += 15
        if contact.get("name") or metrics.get("has_name"):
            score += 10
        return min(100, score)

    def _readability_fallback(self, text: str) -> int:
        words = text.split()
        if not words:
            return 50
        return max(40, min(90, 100 - max(0, len(words) // 100 - 8) * 5))

    def _swot(self, breakdown: dict, parsed: dict, skills: dict) -> tuple[list, list]:
        strengths, weaknesses = [], []
        for k, v in breakdown.items():
            if v >= 75:
                strengths.append(f"Strong {k} ({v}%)")
            elif v < 55:
                weaknesses.append(f"Weak {k} ({v}%) — needs improvement")

        sm = skills.get("skill_match_percent", 0)
        if sm >= 70:
            strengths.append(f"Good skill match ({sm}%)")
        elif sm < 50:
            weaknesses.append("Low skill match vs target role profile")

        for sec in parsed.get("missing_sections", []):
            weaknesses.append(f"Missing {sec} section")

        return strengths[:6], weaknesses[:6]

    def _detailed_report(self, breakdown: dict, missing: list) -> list[dict]:
        report = []
        labels = {
            "formatting": "Formatting & layout",
            "keywords": "Keyword optimization",
            "completeness": "Section completeness",
            "structure": "Document structure",
            "readability": "Readability",
            "contact": "Contact information",
        }
        for key, val in breakdown.items():
            status = (
                "excellent"
                if val >= 80
                else "good"
                if val >= 65
                else "fair"
                if val >= 50
                else "poor"
            )
            report.append({"dimension": labels.get(key, key), "score": val, "status": status})

        if missing:
            report.append(
                {
                    "dimension": "Missing sections",
                    "score": max(0, 100 - len(missing) * 20),
                    "status": "poor",
                    "detail": ", ".join(missing),
                }
            )
        return report

    def _grade(self, score: float) -> str:
        if score >= 85:
            return "A"
        if score >= 72:
            return "B"
        if score >= 58:
            return "C"
        if score >= 45:
            return "D"
        return "F"

    def _strength(self, score: float) -> str:
        if score >= 80:
            return "strong"
        if score >= 65:
            return "moderate"
        if score >= 50:
            return "developing"
        return "needs_work"

