import pytest
from resume_iq.ingestion.models import PreprocessedDocument
from resume_iq.segmentation.segmenter import SectionSegmenter

@pytest.fixture
def segmenter():
    return SectionSegmenter()

def create_doc(lines):
    return PreprocessedDocument(
        source_name="test.pdf",
        source_type="pdf",
        raw_text="\n".join(lines),
        clean_text="\n".join(lines),
        lines=lines
    )

def test_basic_segmentation(segmenter):
    doc = create_doc([
        "John Doe",
        "john@example.com",
        "Experience",
        "Software Engineer at Google",
        "Education",
        "B.S. in Computer Science"
    ])
    
    res = segmenter.segment(doc)
    
    assert "John Doe" in res.contact.lines
    assert "john@example.com" in res.contact.lines
    
    assert "experience" in res.sections
    assert len(res.sections["experience"]) == 1
    assert "Software Engineer at Google" in res.sections["experience"][0].lines
    
    assert "education" in res.sections
    assert "B.S. in Computer Science" in res.sections["education"][0].lines

def test_heading_variations_and_normalization(segmenter):
    doc = create_doc([
        "PROFESSIONAL EXPERIENCE",
        "Did some work",
        "  technical skills  ",
        "Python, Java"
    ])
    
    res = segmenter.segment(doc)
    
    assert "experience" in res.sections
    assert res.sections["experience"][0].original_heading == "PROFESSIONAL EXPERIENCE"
    assert "Did some work" in res.sections["experience"][0].lines
    
    assert "skills" in res.sections
    assert res.sections["skills"][0].original_heading == "technical skills"
    assert "Python, Java" in res.sections["skills"][0].lines

def test_unknown_sections(segmenter):
    doc = create_doc([
        "CERTIFICATIONS",
        "AWS Certified Developer",
        "AWARDS",
        "Best Employee 2023"
    ])
    
    res = segmenter.segment(doc)
    assert "other" in res.sections
    assert len(res.sections["other"]) == 2
    
    # Check the original headings are preserved for unknown sections
    headings = [s.original_heading for s in res.sections["other"]]
    assert "CERTIFICATIONS" in headings
    assert "AWARDS" in headings

def test_false_positives(segmenter):
    doc = create_doc([
        "John Doe",
        "Experience",
        "PYTHON DEVELOPER",
        "Worked hard",
        "Education",
        "ABC UNIVERSITY",
        "Graduated 2023"
    ])
    
    res = segmenter.segment(doc)
    
    # "PYTHON DEVELOPER" should NOT create a new section, it should be in experience
    assert "PYTHON DEVELOPER" in res.sections["experience"][0].lines
    
    # "ABC UNIVERSITY" should NOT create a new section, it should be in education
    assert "ABC UNIVERSITY" in res.sections["education"][0].lines

def test_multiple_sections_of_same_type(segmenter):
    doc = create_doc([
        "Projects",
        "Project A",
        "Academic Projects",
        "Project B"
    ])
    
    res = segmenter.segment(doc)
    
    # Both match 'projects', so they should be two separate blocks in the list
    assert len(res.sections["projects"]) == 2
    assert "Project A" in res.sections["projects"][0].lines
    assert "Project B" in res.sections["projects"][1].lines

def test_empty_line_cleanup(segmenter):
    doc = create_doc([
        "",
        "John Doe",
        "",
        "Experience",
        "",
        "Job",
        ""
    ])
    
    res = segmenter.segment(doc)
    
    # The pre/post blank lines should be stripped from the final lists
    assert res.contact.lines == ["John Doe"]
    assert res.sections["experience"][0].lines == ["Job"]

def test_empty_document(segmenter):
    doc = create_doc([])
    res = segmenter.segment(doc)
    # Should not crash, just empty contact
    assert len(res.contact.lines) == 0
    assert len(res.sections) == 0
