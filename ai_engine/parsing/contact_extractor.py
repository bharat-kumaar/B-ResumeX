"""Extract contact block and identity fields."""

import re
from typing import Any


class ContactExtractor:
    EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_RE = re.compile(
        r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{3,4}(?:[\s\-]?\d{2,4})?"
    )
    LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?", re.I)
    GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?", re.I)

    def extract(self, text: str, lines: list[str], nlp_doc=None) -> dict[str, Any]:
        email = self._first(self.EMAIL_RE, text)
        phone = self._best_phone(text)
        linkedin = self._first(self.LINKEDIN_RE, text)
        github = self._first(self.GITHUB_RE, text)
        name = self._extract_name(lines, nlp_doc, email)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "location": self._extract_location(lines[:8]),
        }

    def _first(self, pattern: re.Pattern, text: str) -> str | None:
        m = pattern.search(text)
        return m.group(0).strip() if m else None

    def _best_phone(self, text: str) -> str | None:
        candidates = []
        for m in self.PHONE_RE.finditer(text):
            raw = m.group(0).strip()
            digits = re.sub(r"\D", "", raw)
            if 10 <= len(digits) <= 15:
                candidates.append(raw)
        return candidates[0] if candidates else None

    def _extract_name(self, lines: list[str], nlp_doc, email: str | None) -> str | None:
        if nlp_doc is not None:
            for ent in nlp_doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) <= 5:
                    return ent.text.strip()

        for line in lines[:8]:
            candidate = line.split("\n")[0].strip()
            if email and email in candidate:
                continue
            if "@" in candidate or "http" in candidate.lower() or self.PHONE_RE.search(candidate):
                continue
            if re.match(r"^[\w\s\.\-']{3,50}$", candidate) and not candidate.lower().startswith(
                ("resume", "curriculum", "cv", "summary", "objective")
            ):
                words = candidate.split()
                if 2 <= len(words) <= 5 and sum(w[0].isupper() for w in words if w) >= len(words) - 1:
                    return candidate
        first = lines[0].split("\n")[0].strip() if lines else ""
        return first if first and len(first) < 50 and "@" not in first else None

    def _extract_location(self, header_lines: list[str]) -> str | None:
        loc_re = re.compile(
            r"^[A-Za-z\s]+,\s*[A-Z]{2,}(?:\s+\d{5})?$|^[A-Za-z\s]+,\s*[A-Za-z\s]+$",
        )
        for line in header_lines:
            if loc_re.match(line.strip()) and "@" not in line:
                return line.strip()
        return None
