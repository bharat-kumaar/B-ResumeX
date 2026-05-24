"""Extract skills from dedicated skills section lines."""

import re


def parse_skills_block(block: str) -> list[str]:
    if not block:
        return []
    skills = set()
    # Split on common delimiters
    chunks = re.split(r"[,;|•\n/]", block)
    for ch in chunks:
        s = ch.strip().lower()
        s = re.sub(r"^[\-\*●]\s*", "", s)
        if 2 <= len(s) <= 40 and not s.isdigit():
            if re.match(r"^[a-z0-9\s\+\.#]+$", s):
                skills.add(s)
    return sorted(skills)
