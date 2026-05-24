"""Semantic + taxonomy skill detection (more accurate)."""

import re
from typing import Any

from ai_engine.skill_taxonomy import RECOMMENDED_SKILLS, SKILL_TAXONOMY
from ai_engine.parsing.skills_line_parser import parse_skills_block


class SkillDetector:
    _TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9\+/\.]+", re.IGNORECASE)

    def detect(self, text: str, skills_section: str = "") -> dict[str, Any]:
        combined = f"{text}\n{skills_section}".lower()

        found: dict[str, list[str]] = {}
        all_found: set[str] = set()

        # Explicit skills from skills section.
        for s in parse_skills_block(skills_section):
            all_found.add(self._canon(s))
            found.setdefault("from_section", []).append(self._canon(s))

        # Build a lightweight token index for robust multi-word matching.
        # Example: tokens allow matching "machine learning" even if line breaks/symbols exist.
        tokens = [t for t in self._TOKEN_SPLIT_RE.split(combined) if t]
        token_stream = " ".join(tokens)

        for category, skills in SKILL_TAXONOMY.items():
            matched: list[str] = []
            for skill in skills:
                canon = self._canon(skill)

                if self._match_skill(skill, canon, combined, token_stream):
                    matched.append(canon)
                    all_found.add(canon)

            if matched:
                found[category] = sorted(set(found.get(category, []) + matched))

        if found.get("from_section"):
            found["from_section"] = sorted(set(found["from_section"]))

        all_sorted = sorted(all_found)
        missing = [s for s in RECOMMENDED_SKILLS if self._canon(s) not in all_found][:10]

        match_pct = self._match_percent(all_found)

        return {
            "categorized": {k: v for k, v in found.items() if k != "from_section"},
            "section_skills": found.get("from_section", []),
            "all_skills": all_sorted,
            "total_count": len(all_sorted),
            "missing_recommended": missing,
            "density_score": min(100, len(all_sorted) * 5),
            "skill_match_percent": match_pct,
        }

    def _canon(self, s: str) -> str:
        s = (s or "").strip().lower()
        s = s.replace("-", " ")
        s = re.sub(r"\s+", " ", s)
        return s

    def _match_skill(self, raw_skill: str, canon_skill: str, combined: str, token_stream: str) -> bool:
        """Match skill using both regex and token-stream substring matching."""

        # 1) Direct regex boundary match for single-token skills.
        skill_parts = canon_skill.split()
        if len(skill_parts) == 1:
            sk = re.escape(skill_parts[0])
            # Avoid matching inside longer words.
            return re.search(rf"(?<![a-z0-9]){sk}(?![a-z0-9])", combined, re.IGNORECASE) is not None

        # 2) Multi-word match:
        #    - normalize separators and allow arbitrary whitespace/symbols between words
        parts = [re.escape(p) for p in skill_parts]
        pattern = r"\b" + r"\s+".join(parts) + r"\b"

        # Allow symbols/newlines between words: replace spaces in pattern with \W+
        pattern2 = r"\b" + r"\W+".join(parts) + r"\b"

        if re.search(pattern, combined, re.IGNORECASE):
            return True
        if re.search(pattern2, combined, re.IGNORECASE):
            return True

        # 3) Token stream (robust to OCR punctuation): check for phrase as substring.
        # token_stream contains only [a-z0-9+/\.] tokens separated by spaces.
        phrase = " ".join(skill_parts)
        return phrase in token_stream

    def _match_percent(self, found: set[str]) -> float:
        target = {self._canon(s) for s in RECOMMENDED_SKILLS}
        if not target:
            return 0.0
        matched = len({f for f in found if f in target})
        return round(min(100.0, (matched / len(target)) * 100.0), 1)

