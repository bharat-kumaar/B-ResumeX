"""Extract achievements and measurable outcomes."""

import re
from typing import Any

ACHIEVEMENT_MARKERS = re.compile(
    r"\b(achieved|awarded|won|ranked|certified|published|patent|honor|dean\'?s list|"
    r"scholarship|fellowship|increased|reduced|improved|saved|generated)\b",
    re.I,
)
METRIC_RE = re.compile(r"\b\d+%|\$\d+|\d+\+?\s*(?:users|customers|clients|projects)\b", re.I)


class AchievementParser:
    def parse(self, text: str, experience: list[dict]) -> list[dict[str, str]]:
        achievements = []

        for block in re.split(r"\n(?=[\-\•\*]|\d+\.)", text):
            line = block.strip()
            if not line:
                continue
            if ACHIEVEMENT_MARKERS.search(line) or METRIC_RE.search(line):
                if len(line) > 20:
                    achievements.append({
                        "title": line[:80],
                        "detail": line[:300],
                    })

        for exp in experience:
            for bullet in exp.get("bullets", []):
                if METRIC_RE.search(bullet) and bullet not in [a["detail"] for a in achievements]:
                    achievements.append({"title": "Impact", "detail": bullet[:300]})

        seen = set()
        unique = []
        for a in achievements:
            key = a["detail"][:60]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        return unique[:12]
