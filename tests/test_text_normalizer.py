from ai_engine.parsing.text_normalizer import normalize


def test_normalize_fixes_hyphenation_and_spacing():
    raw = "Experi-\nence and  spaces\n\n\n plus\nnewline"
    out = normalize(raw)

    assert "Experience" in out
    assert "\n\n" in out
    assert "  " not in out

