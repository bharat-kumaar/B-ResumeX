"""Dedicated education block parser — high accuracy."""

import re
from typing import Any

DEGREE_RE = re.compile(
    r"\b(B\.?\s*S\.?|B\.?\s*A\.?|B\.?\s*Tech|M\.?\s*S\.?|M\.?\s*A\.?|M\.?\s*Tech|"
    r"MBA|Ph\.?\s*D\.?|Bachelor(?:'s)?|Master(?:'s)?|Associate|BSc|MSc|BE|BTech)\b",
    re.I,
)
FIELD_RE = re.compile(
    r"\b(Computer Science|Engineering|Information Technology|Business|"
    r"Data Science|Mathematics|Physics|Chemistry|Economics|Finance)\b",
    re.I,
)
INSTITUTION_RE = re.compile(
    r"\b(University|College|Institute|School|Academy|IIT|NIT|MIT|Polytechnic)\b",
    re.I,
)
YEAR_RANGE = re.compile(
    r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2}|Present|Current)\b",
    re.I,
)
YEAR_SINGLE = re.compile(r"\b((?:19|20)\d{2})\b")
GPA_RE = re.compile(r"\bGPA\s*[:\s]?\s*([0-4]\.\d{1,2}|\d\.\d{1,2}/4\.?0?)\b", re.I)


class EducationParser:
    def parse(self, block: str, full_text: str = "") -> list[dict[str, Any]]:
        if not block.strip():
            block = self._extract_block(full_text)
        if not block.strip():
            return []

        entries = []
        chunks = re.split(r"\n{2,}|\n(?=[\-\•\*]|\d+\.)", block.strip())
        if len(chunks) <= 1:
            chunks = [ln for ln in block.splitlines() if ln.strip()]

        for chunk in chunks:
            entry = self._parse_chunk(chunk.strip())
            if entry:
                entries.append(entry)

        if not entries and block.strip():
            entries.append(self._parse_chunk(block.strip()))

        return entries[:8]

    def _extract_block(self, text: str) -> str:
        m = re.search(
            r"(?is)(?:^|\n)\s*(?:education|academic\s+background|qualifications)\s*\n"
            r"(.*?)(?=\n\s*(?:experience|employment|skills|projects|certifications|work)\b|\Z)",
            text,
        )
        return m.group(1).strip() if m else ""

    def _parse_chunk(self, text: str) -> dict[str, Any] | None:
        if len(text) < 4:
            return None

        degree = self._degree(text)
        field = self._field(text)
        institution = self._institution(text, degree)
        years = self._years(text)
        gpa_m = GPA_RE.search(text)

        if not any([degree, institution, years]):
            return None

        degree_full = degree or "Degree"
        if field and field.lower() not in degree_full.lower():
            degree_full = f"{degree_full} in {field}"

        return {
            "degree": degree_full,
            "field": field,
            "institution": institution,
            "years": years,
            "gpa": gpa_m.group(0) if gpa_m else None,
            "detail": text[:400],
            "title": self._title(degree_full, institution, years),
        }

    def _degree(self, text: str) -> str | None:
        m = DEGREE_RE.search(text)
        return m.group(0).strip() if m else None

    def _field(self, text: str) -> str | None:
        m = FIELD_RE.search(text)
        return m.group(0).strip() if m else None

    def _institution(self, text: str, degree: str | None) -> str | None:
        if INSTITUTION_RE.search(text):
            # "B.S. CS, State University, 2019"
            parts = [p.strip() for p in text.split(",")]
            for p in parts:
                if INSTITUTION_RE.search(p) and not DEGREE_RE.match(p):
                    return p[:120]
            m = INSTITUTION_RE.search(text)
            start = m.start()
            snippet = text[start : start + 80]
            return snippet.split(",")[0].strip()[:120]

        parts = [p.strip() for p in text.split(",") if p.strip()]
        for p in reversed(parts):
            if YEAR_SINGLE.fullmatch(p):
                continue
            if degree and degree.lower() in p.lower():
                continue
            if len(p) > 6:
                return p[:120]
        return None

    def _years(self, text: str) -> str | None:
        m = YEAR_RANGE.search(text)
        if m:
            return m.group(0)
        years = YEAR_SINGLE.findall(text)
        if not years:
            return None
        if len(years) == 1:
            return years[0]
        return f"{years[0]} – {years[-1]}"

    def _title(self, degree: str, inst: str | None, years: str | None) -> str:
        parts = [degree]
        if inst:
            parts.append(inst)
        if years:
            parts.append(f"({years})")
        return " — ".join(parts[:2]) + (f" ({years})" if years and len(parts) > 2 else "")
