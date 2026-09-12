import pytest
from resume_iq.preprocessing.cleaner import TextCleaner

def test_whitespace_normalization():
    raw = "John\tDoe  is   here.\n\n\nSoftware   Engineer"
    clean = TextCleaner.clean(raw)
    lines = clean.splitlines()
    assert "John Doe is here." in lines
    assert "Software Engineer" in lines

def test_bullet_normalization():
    raw = "Skills:\n* Python\n- Java\n• C++\n● React"
    clean = TextCleaner.clean(raw)
    lines = clean.splitlines()
    assert "• Python" in lines
    assert "• Java" in lines
    assert "• C++" in lines
    assert "• React" in lines

def test_special_characters():
    raw = "Hello\x00World\nValid unicode: éñ"
    clean = TextCleaner.clean(raw)
    assert "HelloWorld" in clean
    assert "Valid unicode: éñ" in clean

def test_noise_reduction():
    raw = "Jane Smith | Resume\nPage 1 of 2\nExperience\nJane Smith | Resume\nPage 2 of 2\nEducation"
    clean = TextCleaner.clean(raw)
    lines = clean.splitlines()
    # The header "Jane Smith | Resume" is kept since we only aggressively remove explicit "Page X of Y" for now,
    # as per the heuristic.
    assert "Page 1 of 2" not in clean
    assert "Page 2 of 2" not in clean
    assert "Experience" in clean

def test_clean_empty_lines():
    raw = "\n\nFirst\n\n\n\nSecond\n\n"
    clean = TextCleaner.clean(raw)
    assert clean == "First\n\nSecond"
