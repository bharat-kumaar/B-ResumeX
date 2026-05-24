"""Keyword and phrase extraction for ATS matching."""

import re
from collections import Counter
from typing import Any

from ai_engine.skill_taxonomy import ACTION_VERBS, SKILL_TAXONOMY


class KeywordExtractor:
    STOP = frozenset(
        "a an the and or for with to of in on at by from is was are be have has had "
        "this that it as your you our their".split()
    )

    def extract(self, text: str, skills_found: set[str]) -> dict[str, Any]:
        lower = text.lower()
        words = re.findall(r"[a-z][a-z0-9+#.]{1,24}", lower)
        freq = Counter(w for w in words if w not in self.STOP and len(w) > 2)

        top_keywords = [w for w, _ in freq.most_common(25) if w not in skills_found][:15]
        action_verbs_used = [v for v in ACTION_VERBS if re.search(rf"\b{re.escape(v)}\b", lower)]
        bigrams = self._top_bigrams(lower)

        return {
            "top_keywords": top_keywords,
            "action_verbs_used": action_verbs_used[:12],
            "keyword_density": round(len(set(words)) / max(len(words), 1) * 100, 1),
            "top_phrases": bigrams[:10],
        }

    def _top_bigrams(self, lower: str) -> list[str]:
        words = re.findall(r"[a-z]{3,}", lower)
        bigrams = Counter(
            f"{words[i]} {words[i+1]}"
            for i in range(len(words) - 1)
            if words[i] not in self.STOP and words[i + 1] not in self.STOP
        )
        return [p for p, _ in bigrams.most_common(10)]

    def skill_match_percent(self, found_skills: set[str], target_role: str = "software") -> float:
        """Match % against role skill profile (fuzzy on subset)."""
        profiles = {
            "software": set(
                SKILL_TAXONOMY["languages"]
                + SKILL_TAXONOMY["frameworks"][:10]
                + SKILL_TAXONOMY["cloud_devops"][:6]
                + ["git", "sql", "agile", "problem solving", "communication"]
            ),
            "data": set(SKILL_TAXONOMY["data_ai"] + ["python", "sql", "pandas", "machine learning"]),
        }
        target = profiles.get(target_role, profiles["software"])
        if not target:
            return 0.0
        matched = len(found_skills & target)
        partial = sum(1 for t in target if any(t in f or f in t for f in found_skills))
        score = (matched * 2 + partial) / (len(target) * 2) * 100
        return round(min(100, score), 1)
