import pytest
from resume_iq.extraction.skill_extractor import SkillExtractor, SkillOntology

def test_skill_ontology_load():
    # It should safely load the local json file
    ontology = SkillOntology()
    assert len(ontology.skills_list) > 0
    assert "python" in ontology.canonical_map
    assert "reactjs" in ontology.canonical_map

def test_skill_extractor_exact():
    extractor = SkillExtractor()
    skills = extractor.extract_from_text("I know Python and Java.", "skills")
    names = [s.canonical_name for s in skills]
    assert "Python" in names
    assert "Java" in names

def test_skill_extractor_alias():
    extractor = SkillExtractor()
    skills = extractor.extract_from_text("I use React.js and NodeJS", "skills")
    names = [s.canonical_name for s in skills]
    assert "React" in names
    assert "Node.js" in names

def test_skill_extractor_punctuation():
    extractor = SkillExtractor()
    skills = extractor.extract_from_text("Programming in C++ and C#", "skills")
    names = [s.canonical_name for s in skills]
    assert "C++" in names
    assert "C#" in names
    assert "C" not in names # Avoid false positive for C from C++
    
def test_skill_extractor_false_positives():
    extractor = SkillExtractor()
    # Check that boundaries prevent false positives
    # "Reacting" shouldn't match "React"
    # "Go" shouldn't match "Good"
    # "C" shouldn't match "Cat"
    skills = extractor.extract_from_text("I am reacting to a good cat.", "skills")
    names = [s.canonical_name for s in skills]
    assert "React" not in names
    assert "Go" not in names
    assert "C" not in names

def test_skill_extractor_deduplication():
    extractor = SkillExtractor()
    # Mentions Python multiple times and as different aliases
    skills = extractor.extract_from_text("Python is great. Python 3 is also Python.", "experience")
    
    # Should only return one Skill object for Python
    python_skills = [s for s in skills if s.canonical_name == "Python"]
    assert len(python_skills) == 1
    
    python_skill = python_skills[0]
    # Should record the matched aliases
    # Note: the regex match is case insensitive but preserves original text match.
    # Actually, the matches would be "Python" and "Python 3".
    assert "Python" in python_skill.aliases_matched
    assert "Python 3" in python_skill.aliases_matched
    
    # Should record multiple evidence points
    assert len(python_skill.evidence) >= 2
