"""Experience entries with roles, dates, bullets."""

import re
from typing import Any

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
DATE_RANGE = re.compile(
    rf"\b{MONTH}\s+\d{{4}}\s*[-–—]\s*(?:{MONTH}\s+)?(?:\d{{4}}|Present|Current)\b",
    re.I,
)
YEAR_RANGE = re.compile(r"\b(20|19)\d{2}\s*[-–—]\s*((?:20|19)\d{2}|Present|Current)\b", re.I)
COMPANY_HINT = re.compile(r"\b(Inc\.|LLC|Ltd\.|Corp\.|Company|Technologies|Solutions)\b", re.I)


class ExperienceParser:
    def parse(self, block: str) -> list[dict[str, Any]]:
        if not block.strip():
            return []

        entries = []
        lines = block.splitlines()
        current_role: list[str] = []
        bullets: list[str] = []

        def flush():
            if not current_role and not bullets:
                return
            entries.append(self._build_entry(current_role, bullets))

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            is_bullet = bool(re.match(r"^[\-\•\*●]\s+", stripped) or re.match(r"^\d+[\.\)]\s+", stripped))
            if is_bullet:
                bullets.append(re.sub(r"^[\-\•\*●\d\.\)]\s+", "", stripped))
            elif self._is_role_header(stripped) and (bullets or current_role):
                flush()
                current_role = [stripped]
                bullets = []
            else:
                if bullets:
                    flush()
                    bullets = []
                current_role.append(stripped)

        flush()

        if not entries and block.strip():
            entries.append({
                "title": "Experience",
                "company": None,
                "dates": None,
                "bullets": [block.strip()[:400]],
                "detail": block.strip()[:500],
            })
        return entries[:10]

    def _is_role_header(self, line: str) -> bool:
        if DATE_RANGE.search(line) or YEAR_RANGE.search(line):
            return True
        if "|" in line and len(line) < 120:
            return True
        if COMPANY_HINT.search(line):
            return True
        return len(line) < 80 and line[0].isupper()

    def _build_entry(self, header_lines: list[str], bullets: list[str]) -> dict[str, Any]:
        header = " | ".join(header_lines) if header_lines else "Role"
        dates = None
        for part in header_lines:
            d = DATE_RANGE.search(part) or YEAR_RANGE.search(part)
            if d:
                dates = d.group(0)
                break

        title = header_lines[0] if header_lines else "Position"
        company = header_lines[1] if len(header_lines) > 1 else None

        enhanced_bullets = bullets or [header]
        return {
            "title": title[:100],
            "company": company[:100] if company else None,
            "dates": dates,
            "bullets": enhanced_bullets[:8],
            "detail": " ".join(enhanced_bullets)[:500],
        }
