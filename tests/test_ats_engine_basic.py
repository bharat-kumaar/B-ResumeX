from ai_engine.ats_engine import ATSEngine


def test_ats_engine_scores_are_in_bounds():
    engine = ATSEngine()
    text = "Name: John Doe\nEmail: john@example.com\nPython developer. Built APIs with Django."
    parsed = {
        "metrics": {
            "word_count": len(text.split()),
            "bullet_count": 2,
            "readability_score": 75,
            "has_email": True,
        },
        "missing_sections": [],
        "sections_detected": ["summary", "skills", "experience", "education"],
        "experience": [{"bullets": ["Implemented REST APIs with Python"]}],
        "education": [{"degree": "B.Tech", "institution": "Uni", "years": "2022"}],
        "contact": {"email": "john@example.com"},
    }
    skills = {"total_count": 10, "skill_match_percent": 80}

    res = engine.score(text, parsed, skills)
    assert 0 <= res["overall"] <= 100
    assert set(res["breakdown"].keys()) >= {"formatting", "keywords", "completeness", "structure", "readability", "contact"}

