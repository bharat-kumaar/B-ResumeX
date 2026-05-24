"""Advanced resume parser — NLP + regex orchestration.

Phase 1 upgrade:
- spaCy-assisted weak semantic section detection (best-effort; always with fallbacks)
- fuzzy heading matching (rapidfuzz if available, difflib fallback)
- per-section confidence scoring and parse confidence refinement
- regex fallback logic stays in place to prevent regressions
"""

import re
from typing import Any

from ai_engine.parser import ResumeParser
from ai_engine.parsing.nlp_loader import get_nlp, nlp_mode
from ai_engine.parsing.text_normalizer import normalize
from ai_engine.parsing.contact_extractor import ContactExtractor
from ai_engine.parsing.education_parser import EducationParser
from ai_engine.parsing.experience_parser import ExperienceParser
from ai_engine.parsing.achievement_parser import AchievementParser
from ai_engine.parsing.keyword_extractor import KeywordExtractor
from ai_engine.skill_detector import SkillDetector
from ai_engine.section_extractor import SECTION_ALIASES

EXPERIENCE_FALLBACK = re.compile(
    r"(?is)(?:^|\n)\s*(?:experience|work\s+experience|employment|work\s+history)\s*\n"
    r"(.*?)(?=\n\s*(?:education|skills|projects|certifications)\b|\Z)",
)


class AdvancedResumeParser:
    REQUIRED = ["experience", "education", "skills", "summary"]
    OPTIONAL = ["projects", "certifications", "achievements"]

    def __init__(self):
        self.file_parser = ResumeParser()
        self.contact = ContactExtractor()
        self.education = EducationParser()
        self.experience = ExperienceParser()
        self.achievements = AchievementParser()
        self.keywords = KeywordExtractor()
        self.skills = SkillDetector()

    def parse_file(self, filepath: str) -> dict[str, Any]:
        doc = self.file_parser.parse(filepath)
        return self.parse_text(doc["raw_text"], doc)

    def parse_text(self, text: str, doc: dict | None = None) -> dict[str, Any]:
        text = normalize(text)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        nlp_doc = None
        nlp = get_nlp()
        if nlp and len(text) < 80000:
            try:
                nlp_doc = nlp(text[:20000])
            except Exception:
                nlp_doc = None

        section_blocks, section_confidence = self._split_sections(lines, nlp_doc)

        contact = self.contact.extract(text, lines, nlp_doc)

        exp_block = section_blocks.get("experience", "")
        if not exp_block.strip():
            exp_block = self._fallback_experience(text)
        experience = self.experience.parse(exp_block)

        education = self.education.parse(section_blocks.get("education", ""), text)
        projects = self._parse_projects(section_blocks.get("projects", ""))
        certifications = self._parse_list(section_blocks.get("certifications", ""))
        achievement_list = self.achievements.parse(text, experience)

        skill_data = self.skills.detect(text, section_blocks.get("skills", ""))
        keywords = self.keywords.extract(text, set(skill_data.get("all_skills", [])))
        skill_data["keywords_meta"] = keywords

        summary = (
            section_blocks.get("summary")
            or section_blocks.get("objective")
            or self._infer_summary_from_preamble(section_blocks.get("preamble", ""))
        )[:700]

        sections_found = self._section_status(section_blocks, contact, education, experience, summary)

        metrics = {
            "has_email": bool(contact.get("email")),
            "has_phone": bool(contact.get("phone")),
            "has_linkedin": bool(contact.get("linkedin")),
            "has_github": bool(contact.get("github")),
            "has_name": bool(contact.get("name")),
            "bullet_count": len(re.findall(r"^[\-\•\*]\s+", text, re.M)) + text.count("•"),
            "word_count": len(text.split()),
            "line_count": len(lines),
            "readability_score": self._readability(text),
            "parse_confidence": self._confidence(
                sections_found, contact, education, experience, section_confidence
            ),
        }

        return {
            "document": doc or {"raw_text": text, "word_count": metrics["word_count"]},
            "contact": contact,
            "summary": summary,
            "sections_detected": sections_found["present"],
            "section_status": sections_found["status"],
            "missing_sections": sections_found["missing"],
            "experience": experience,
            "education": education,
            "projects": projects,
            "certifications": certifications,
            "achievements": achievement_list,
            "skills_raw": section_blocks.get("skills", ""),
            "metrics": metrics,
            "keywords": keywords,
            "skills": skill_data,
            "parse_meta": {
                "nlp": nlp_mode(),
                "sections_found": list(section_blocks.keys()),
                "section_confidence": section_confidence,
            },
        }

    def _split_sections(self, lines: list[str], nlp_doc) -> tuple[dict[str, str], dict[str, float]]:
        buckets: dict[str, list[str]] = {}
        current = "preamble"
        confidence: dict[str, float] = {}

        for line in lines:
            key, conf = self._match_header_semantic(line, nlp_doc)
            if key:
                current = key
                buckets.setdefault(current, [])
                confidence[current] = max(confidence.get(current, 0.0), conf)
            else:
                buckets.setdefault(current, []).append(line)

        section_blocks = {k: "\n".join(v) for k, v in buckets.items() if v}
        for sec in set(self.REQUIRED + self.OPTIONAL):
            confidence.setdefault(sec, 0.0)

        return section_blocks, confidence

    def _match_header_semantic(self, line: str, nlp_doc) -> tuple[str | None, float]:
        """Return (section_key, confidence) using fuzzy matching + best-effort semantic signals."""
        norm = (line or "").lower().strip().rstrip(":").strip()
        if not norm or len(norm) > 55:
            return None, 0.0

        best_key = None
        best_score = 0.0

        # fuzzy heading matching
        try:
            from rapidfuzz import fuzz  # type: ignore

            for key, aliases in SECTION_ALIASES.items():
                for alias in aliases:
                    a = alias.lower().strip().rstrip(":")
                    s = fuzz.token_set_ratio(norm, a)
                    if s > best_score:
                        best_score = float(s)
                        best_key = key
        except Exception:
            import difflib

            for key, aliases in SECTION_ALIASES.items():
                for alias in aliases:
                    a = alias.lower().strip().rstrip(":")
                    s = difflib.SequenceMatcher(None, norm, a).ratio() * 100.0
                    if s > best_score:
                        best_score = float(s)
                        best_key = key

        if best_key and best_score >= 82:
            conf = min(0.98, 0.45 + (best_score / 100.0) * 0.55)
            return best_key, conf

        # uppercase short heading heuristic
        if (line or "").isupper() and 3 < len(line) < 40:
            for key, aliases in SECTION_ALIASES.items():
                for alias in aliases:
                    if alias.lower() in norm:
                        return key, 0.78

        # spaCy weak semantic signal (safe keyword presence)
        if nlp_doc is not None:
            for key, aliases in SECTION_ALIASES.items():
                alias_hits = 0
                for alias in aliases:
                    parts = [w for w in alias.lower().split() if len(w) > 2]
                    if parts and sum(1 for w in parts if w in norm) >= max(1, len(parts) - 1):
                        alias_hits += 1
                if alias_hits >= 2:
                    return key, 0.62

        # cheap fallback containment
        for key, aliases in SECTION_ALIASES.items():
            for alias in aliases:
                a = alias.lower()
                if norm == a or a in norm:
                    return key, 0.58

        return None, 0.0

    def _fallback_experience(self, text: str) -> str:
        m = EXPERIENCE_FALLBACK.search(text)
        return m.group(1).strip() if m else ""

    def _infer_summary_from_preamble(self, preamble: str) -> str:
        if not preamble:
            return ""
        paras = [p.strip() for p in preamble.split("\n\n") if len(p.strip()) > 60]
        for p in paras:
            low = p.lower()
            if any(w in low for w in ("experience", "engineer", "developer", "professional", "years")):
                return p
        return paras[0] if paras else ""

    def _section_status(self, blocks, contact, education, experience, summary) -> dict:
        present, status = [], {}
        checks = {
            "summary": bool(summary and len(summary) > 40),
            "skills": bool(blocks.get("skills", "").strip()),
            "experience": bool(experience),
            "education": bool(education),
            "projects": bool(blocks.get("projects", "").strip()),
            "certifications": bool(blocks.get("certifications", "").strip()),
            "achievements": bool(blocks.get("achievements", "").strip()),
        }

        for sec in self.REQUIRED + self.OPTIONAL:
            ok = checks.get(sec, False)
            status[sec] = "found" if ok else "missing"
            if ok:
                present.append(sec)

        status["contact"] = (
            "found"
            if contact.get("email") and contact.get("phone")
            else ("partial" if contact.get("email") or contact.get("phone") else "missing")
        )

        missing = [s for s in self.REQUIRED if status.get(s) == "missing"]
        return {"present": present, "status": status, "missing": missing}

    def _confidence(self, sections, contact, education, experience, section_confidence: dict[str, float]) -> int:
        base = 35

        heading_present = 0.0
        if sections["present"]:
            for sec in sections["present"]:
                heading_present += section_confidence.get(sec, 0.0)
            heading_present = heading_present / len(sections["present"])  # avg

        extraction_bonus = 0.0
        extraction_bonus += 10 if contact.get("name") else 0
        extraction_bonus += 10 if education else 0
        extraction_bonus += 15 if experience else 0
        extraction_bonus += 8 if sections.get("present") else 0

        score = base + heading_present * 30 + extraction_bonus
        return int(max(0, min(100, score)))

    def _parse_projects(self, block: str) -> list[dict]:
        if not block:
            return []
        items = []
        for chunk in re.split(r"\n(?=[\-\•\*]|\n[A-Z][a-z])", block):
            chunk = chunk.strip()
            if len(chunk) < 12:
                continue
            lines = chunk.splitlines()
            items.append(
                {
                    "title": lines[0][:100],
                    "detail": " ".join(lines[1:])[:400] if len(lines) > 1 else chunk[:400],
                    "bullets": [re.sub(r"^[\-\•\*]\s+", "", ln) for ln in lines[1:] if ln.strip()][:6],
                }
            )
        return items[:10]

    def _parse_list(self, block: str) -> list[dict]:
        if not block:
            return []
        return [
            {"title": ln.strip()[:120], "detail": ln.strip()[:300]}
            for ln in block.splitlines()
            if ln.strip()
        ][:12]

    def _readability(self, text: str) -> int:
        words = text.split()
        if not words:
            return 50
        sentences = max(1, len(re.split(r"[.!?]+", text)))
        avg = len(words) / sentences
        score = 88
        if avg > 30:
            score -= 25
        elif avg > 22:
            score -= 12
        if avg < 10:
            score -= 8
        long_words = sum(1 for w in words if len(w) > 14)
        score -= min(15, long_words)
        return max(35, min(100, score))

