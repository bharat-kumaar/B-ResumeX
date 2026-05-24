"""AI Resume Rebuilder — professional ATS-optimized output."""

import re
from typing import Any

from ai_engine.skill_taxonomy import ACTION_VERBS

VERB_ROTATION = ["Developed", "Engineered", "Led", "Implemented", "Optimized", "Delivered", "Architected"]


class ResumeRebuilder:
    WEAK_OPENERS = re.compile(
        r"^(responsible for|duties include|worked on|helped with|involved in|tasked with)\s+",
        re.I,
    )

    def build(self, parsed: dict, skills: dict, ats: dict, suggestions: list) -> dict[str, Any]:
        contact = parsed.get("contact", {})
        return {
            "contact": self._contact(contact),
            "summary": self._summary(parsed, skills),
            "skills": self._skills(skills),
            "experience": self._experience(parsed.get("experience", [])),
            "education": self._education(parsed.get("education", [])),
            "projects": self._projects(parsed.get("projects", [])),
            "certifications": self._certs(parsed.get("certifications", [])),
            "achievements": self._achievements(parsed.get("achievements", [])),
            "meta": {
                "optimized": True,
                "target_ats": round(min(98, ats.get("overall", 70) + 10), 1),
                "version": "3.1",
            },
        }

    def _contact(self, c: dict) -> dict:
        return {
            "name": c.get("name") or "Your Name",
            "email": c.get("email") or "",
            "phone": c.get("phone") or "",
            "linkedin": c.get("linkedin") or "",
            "github": c.get("github") or "",
            "location": c.get("location") or "",
        }

    def _summary(self, parsed: dict, skills: dict) -> str:
        raw = (parsed.get("summary") or "").strip()
        if raw and len(raw) > 90:
            return self._polish(raw)

        top = skills.get("all_skills", [])[:8]
        roles = len(parsed.get("experience", []))
        skill_line = ", ".join(top[:5]) if top else "cross-functional technical delivery"
        years_hint = "3+" if roles >= 2 else "proven"

        return self._polish(
            f"Accomplished professional with {years_hint} years of impact across "
            f"{roles or 1} roles, specializing in {skill_line}. "
            f"Track record of building scalable solutions, collaborating with stakeholders, "
            f"and driving measurable outcomes aligned with business goals."
        )

    def _skills(self, skills: dict) -> dict[str, list[str]]:
        cat = dict(skills.get("categorized", {}))
        section = skills.get("section_skills", [])
        if section:
            cat.setdefault("core", [])
            cat["core"] = sorted(set(cat["core"] + section))[:25]
        return cat or {"core": skills.get("all_skills", [])[:25]}

    def _experience(self, items: list) -> list[dict]:
        out = []
        for i, item in enumerate(items):
            bullets = item.get("bullets") or []
            if not bullets and item.get("detail"):
                bullets = [item["detail"]]
            new_bullets = []
            for j, b in enumerate(bullets[:6]):
                if b.strip():
                    new_bullets.append(self._bullet(b, i * 3 + j))
            title, company = self._split_role(item)
            out.append({
                "title": title,
                "company": company,
                "dates": item.get("dates"),
                "bullets": new_bullets,
            })
        return out

    def _split_role(self, item: dict) -> tuple[str, str | None]:
        title = item.get("title", "Position")
        company = item.get("company")
        if not company and "|" in title:
            parts = [p.strip() for p in title.split("|")]
            return parts[0], parts[1] if len(parts) > 1 else None
        if not company and " at " in title.lower():
            parts = re.split(r"\s+at\s+", title, maxsplit=1, flags=re.I)
            return parts[0], parts[1] if len(parts) > 1 else None
        return title, company

    def _education(self, items: list) -> list[dict]:
        if not items:
            return [{
                "degree": "Bachelor of Science — Major",
                "institution": "University Name",
                "years": "YYYY",
                "gpa": None,
            }]
        result = []
        for e in items:
            inst = e.get("institution") or ""
            if e.get("degree") and inst and e["degree"].lower() in inst.lower():
                inst = self._clean_institution(inst, e.get("degree"))
            result.append({
                "degree": e.get("degree") or "Degree",
                "institution": inst or "Institution",
                "years": e.get("years"),
                "gpa": e.get("gpa"),
            })
        return result

    def _clean_institution(self, inst: str, degree: str) -> str:
        parts = [p.strip() for p in inst.split(",")]
        for p in parts:
            if "university" in p.lower() or "college" in p.lower() or "institute" in p.lower():
                return p
        for p in parts:
            if degree.lower() not in p.lower():
                return p
        return parts[-1] if parts else inst

    def _projects(self, items: list) -> list[dict]:
        return [
            {
                "title": p.get("title", "Project"),
                "bullets": [self._bullet(b, i) for i, b in enumerate((p.get("bullets") or [p.get("detail", "")])[:4]) if b.strip()],
            }
            for p in items
        ]

    def _certs(self, items: list) -> list[str]:
        return list({(i.get("title") or i.get("detail", ""))[:120] for i in items if i.get("title") or i.get("detail")})

    def _achievements(self, items: list) -> list[str]:
        return [self._polish(i.get("detail", i.get("title", ""))) for i in items[:8] if i.get("detail") or i.get("title")]

    def _bullet(self, text: str, verb_idx: int = 0) -> str:
        text = self.WEAK_OPENERS.sub("", text.strip())
        if not text:
            return text
        if not text[0].isupper():
            text = text[0].upper() + text[1:]
        has_verb = any(re.match(rf"^{re.escape(v)}\b", text, re.I) for v in ACTION_VERBS)
        if not has_verb:
            verb = VERB_ROTATION[verb_idx % len(VERB_ROTATION)]
            text = f"{verb} {text[0].lower() + text[1:]}" if len(text) > 8 else f"{verb} key initiatives"
        return self._polish(text)

    def _polish(self, s: str) -> str:
        s = re.sub(r"\s+", " ", s).strip()
        if s and not s.endswith("."):
            s += "."
        return s
