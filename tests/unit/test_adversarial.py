import pytest
from resume_iq.parser import ResumeParser
from resume_iq.models.resume import Resume
from resume_iq.segmentation.segmenter import SectionSegmenter
from resume_iq.ingestion.models import PreprocessedDocument
from resume_iq.extraction.orchestrator import InformationExtractor

def test_adversarial_minimal_resume():
    """TEST A - Minimal Resume"""
    text = "John Doe\njohndoe@email.com\n555-1234"
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    extractor = InformationExtractor()
    
    structured = segmenter.segment(doc)
    resume = extractor.extract(structured)
    
    assert resume.contact.name == "John Doe"
    assert resume.contact.email == "johndoe@email.com"
    # Empty sections shouldn't crash
    assert len(resume.experience) == 0
    assert len(resume.education) == 0
    assert len(resume.skills) == 0

def test_adversarial_unusual_section_ordering():
    """TEST C - Unusual Section Ordering"""
    text = """
    Projects
    - Alpha Project
    
    Skills
    Python, Java
    
    Education
    BSc Computer Science
    
    Experience
    Software Engineer at Google
    
    Summary
    I am a developer.
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    structured = segmenter.segment(doc)
    
    # Should correctly find sections regardless of order
    assert "projects" in structured.sections
    assert "skills" in structured.sections
    assert "education" in structured.sections
    assert "experience" in structured.sections
    assert "summary" in structured.sections

def test_adversarial_unknown_sections():
    """TEST D - Unknown Sections"""
    text = """
    Awards
    Best Developer 2023
    
    Publications
    AI in 2024
    
    Skills
    Python
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    structured = segmenter.segment(doc)
    
    # Awards and Publications are unknown, so they fall under 'other'
    assert "other" in structured.sections
    # Skills is known
    assert "skills" in structured.sections

def test_adversarial_false_heading():
    """TEST E - False Heading Resume"""
    # A job title that looks like a header shouldn't ruin everything if there's no surrounding context
    # Our heuristic checks if the line is short and uppercase, but it needs to match synonyms.
    text = """
    Experience
    PYTHON DEVELOPER
    I developed Python apps.
    
    MACHINE LEARNING ENGINEER
    I built ML pipelines.
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    structured = segmenter.segment(doc)
    
    # "PYTHON DEVELOPER" shouldn't become a section, it should stay in Experience.
    assert "experience" in structured.sections
    assert len(structured.sections["experience"]) == 1 # Just one big block under experience
    
    content = "\n".join(structured.sections["experience"][0].lines)
    assert "PYTHON DEVELOPER" in content

def test_adversarial_multiple_person_entities():
    """TEST F - Multiple PERSON Entities"""
    text = """
    John Doe
    johndoe@email.com
    
    Experience
    Worked with Jane Smith at Google.
    Contacted by Robert Brown.
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    extractor = InformationExtractor()
    
    structured = segmenter.segment(doc)
    resume = extractor.extract(structured)
    
    # Name should be John Doe (prioritized from contact section and matched to email 'john')
    assert resume.contact.name == "John Doe"

def test_adversarial_similar_technologies():
    """TEST G - Similar Technology Names"""
    text = """
    Skills
    Java, JavaScript, C, C++, C#, Go, R, React, React.js, Node.js
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    extractor = InformationExtractor()
    
    structured = segmenter.segment(doc)
    resume = extractor.extract(structured)
    
    skill_names = [s.canonical_name for s in resume.skills]
    
    # Should cleanly distinguish them
    assert "Java" in skill_names
    assert "JavaScript" in skill_names
    assert "C" in skill_names
    assert "C++" in skill_names
    assert "C#" in skill_names
    assert "Go" in skill_names
    # R is intentionally excluded from ontology right now to avoid false positives in basic heuristic
    # React and React.js merge to React
    assert "React" in skill_names
    # Node.js
    assert "Node.js" in skill_names

def test_adversarial_unicode():
    """TEST I - Unicode"""
    text = """
    Jöhn Dœ
    johndoe@email.com
    
    Education
    Üniversity of Mùnïch
    """
    doc = PreprocessedDocument(lines=text.split("\n"), source_name="test", source_type="txt")
    segmenter = SectionSegmenter()
    extractor = InformationExtractor()
    
    structured = segmenter.segment(doc)
    resume = extractor.extract(structured)
    
    assert resume.contact.name == "Jöhn Dœ"
    assert "Üniversity of Mùnïch" in "\n".join(structured.sections["education"][0].lines)
