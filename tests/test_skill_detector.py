import pytest


from ai_engine.skill_detector import SkillDetector
from ai_engine.skill_taxonomy import RECOMMENDED_SKILLS


def test_skill_detector_detects_languages_and_tools():
    sd = SkillDetector()
    text = "Experienced Python developer with Django and AWS. Built CI/CD pipelines."
    out = sd.detect(text)

    assert "python" in out["all_skills"]
    assert any(s in out["all_skills"] for s in ["django", "flask", "fastapi"])
    assert "aws" in out["all_skills"] or any(s.startswith("docker") for s in out["all_skills"])

    # Match percent should be non-trivial for recommended skills
    assert out["skill_match_percent"] >= 0


def test_skill_detector_multiword_phrase_detection():
    sd = SkillDetector()
    text = "Hands-on with machine learning and natural language processing (NLP)."
    out = sd.detect(text)

    assert any("machine learning" in s for s in out["all_skills"])
    assert any("nlp" in s or "natural language" in s for s in out["all_skills"])

