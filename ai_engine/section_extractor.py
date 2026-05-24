"""Extract structured resume sections from raw text."""

import re
from typing import Any

SECTION_ALIASES = {
    "experience": ["experience", "work experience", "employment", "professional experience", "work history"],
    "education": ["education", "academic background", "qualifications"],
    "skills": ["skills", "technical skills", "core competencies", "expertise", "technologies"],
    "projects": ["projects", "personal projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "summary": ["summary", "professional summary", "profile", "about me", "overview"],
    "objective": ["objective", "career objective"],
}


class SectionExtractor:
    """Split resume text into labeled sections and list items."""

    def extract(self, text: str) -> dict[str, Any]:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        sections = self._split_sections(lines)
        return {
            "sections_detected": [k for k in sections if k != "preamble"],
            "experience": self._parse_bullets(sections.get("experience", "")),
            "education": self._parse_bullets(sections.get("education", "")),
            "projects": self._parse_bullets(sections.get("projects", "")),
            "skills_raw": sections.get("skills", ""),
            "summary": (sections.get("summary") or sections.get("objective") or "")[:500],
            "certifications": self._parse_bullets(sections.get("certifications", "")),
        }

    def _is_header(self, line: str) -> str | None:
        normalized = line.lower().strip().rstrip(":").strip()
        for key, aliases in SECTION_ALIASES.items():
            for alias in aliases:
                if normalized == alias or normalized.startswith(alias + " "):
                    return key
        if len(normalized) < 40 and normalized.isupper() and len(normalized) > 3:
            for key, aliases in SECTION_ALIASES.items():
                for alias in aliases:
                    if alias in normalized:
                        return key
        return None

    def _split_sections(self, lines: list[str]) -> dict[str, str]:
        current_key = "preamble"
        buckets: dict[str, list[str]] = {}

        for line in lines:
            header_key = self._is_header(line)
            if header_key:
                current_key = header_key
                buckets.setdefault(current_key, [])
            else:
                buckets.setdefault(current_key, []).append(line)

        return {k: "\n".join(v) for k, v in buckets.items() if v}

    def _parse_bullets(self, block: str) -> list[dict[str, str]]:
        if not block:
            return []
        items = []
        current: list[str] = []
        for line in block.splitlines():
            if re.match(r"^[\-\•\*●○▪]\s+", line) or re.match(r"^\d+[\.\)]\s+", line):
                if current:
                    items.append(self._item_from_lines(current))
                current = [re.sub(r"^[\-\•\*●○▪\d\.\)]\s+", "", line)]
            elif current:
                current.append(line)
            else:
                current = [line]
        if current:
            items.append(self._item_from_lines(current))
        if not items and block.strip():
            chunks = re.split(r"\n{2,}", block.strip())
            for ch in chunks[:8]:
                items.append({"title": ch.split("\n")[0][:120], "detail": ch[:400]})
        return items[:12]

    def _item_from_lines(self, lines: list[str]) -> dict[str, str]:
        title = lines[0][:120]
        detail = " ".join(lines[1:])[:400] if len(lines) > 1 else lines[0][:400]
        return {"title": title, "detail": detail}
