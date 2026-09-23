import pytest
from resume_iq.extraction.regex_extractors import RegexExtractor
from resume_iq.extraction.date_extractors import DateExtractor
from resume_iq.extraction.ner_extractors import NERExtractor
from resume_iq.extraction.orchestrator import InformationExtractor
from resume_iq.segmentation.models import StructuredResume, Section

def test_extract_email():
    assert RegexExtractor.extract_email("Contact me at john.doe+tag@example.co.in please.") == "john.doe+tag@example.co.in"
    assert RegexExtractor.extract_email("No email here") is None

def test_extract_phone():
    # Valid international
    assert RegexExtractor.extract_phone("Call +91 98765 43210") == "+919876543210"
    assert RegexExtractor.extract_phone("+91-98765-43210") == "+919876543210"
    # Ambiguous but valid in default region (IN)
    assert RegexExtractor.extract_phone("9876543210") == "+919876543210"
    # Other country (US)
    assert RegexExtractor.extract_phone("+1 415 555 0100") == "+14155550100"
    # Invalid
    assert RegexExtractor.extract_phone("My zip code is 12345") is None # Too short

def test_extract_urls():
    text = "LinkedIn: linkedin.com/in/johndoe GitHub: github.com/johndoe Website: https://myportfolio.me/about"
    assert RegexExtractor.extract_linkedin(text) == "https://linkedin.com/in/johndoe"
    assert RegexExtractor.extract_portfolio(text) == "https://github.com/johndoe" # picks the first non-linkedin match

def test_extract_dates():
    assert DateExtractor.extract_date_range("Jan 2024 to Present") == ("Jan 2024", "Present")
    assert DateExtractor.extract_date_range("2020 - 2024") == ("2020", "2024")
    assert DateExtractor.extract_date_range("01/2022") == ("01/2022", None)

def test_ner_candidate_name():
    # Provide email to verify heuristic
    contact_lines = [
        "Jane Smith",
        "jane.smith@example.com",
        "Data Scientist"
    ]
    name = NERExtractor.extract_candidate_name(contact_lines, "jane.smith@example.com")
    assert name == "Jane Smith"
    
    # Fallback to first line if NER fails to identify (e.g., all caps)
    contact_lines_caps = ["JANE SMITH", "jane@email.com"]
    name_caps = NERExtractor.extract_candidate_name(contact_lines_caps, "jane@email.com")
    assert name_caps == "JANE SMITH"

def test_orchestrator():
    structured = StructuredResume()
    structured.contact = Section(
        canonical_name="contact", 
        original_heading=None,
        lines=["John Doe", "john@example.com", "linkedin.com/in/john"]
    )
    
    exp_sec = Section(canonical_name="experience", original_heading="Experience", lines=[
        "Google Inc.",
        "Software Engineer",
        "Jan 2024 - Present",
        "Did some coding in Python."
    ])
    structured.add_section(exp_sec)
    
    edu_sec = Section(canonical_name="education", original_heading="Education", lines=[
        "Stanford University",
        "B.Tech in Computer Science",
        "2020 - 2024"
    ])
    structured.add_section(edu_sec)
    
    extractor = InformationExtractor()
    resume = extractor.extract(structured)
    
    # Contact
    assert resume.contact.name == "John Doe"
    assert resume.contact.email == "john@example.com"
    assert resume.contact.linkedin == "https://linkedin.com/in/john"
    
    # Experience
    assert len(resume.experience) == 1
    exp = resume.experience[0]
    assert exp.company == "Google Inc"
    assert exp.job_title == "Software Engineer"
    assert exp.start_date == "Jan 2024"
    assert exp.end_date == "Present"
    assert exp.dates == "Jan 2024 - Present"
    
    # Education
    assert len(resume.education) == 1
    edu = resume.education[0]
    assert edu.institution == "Stanford University"
    assert edu.degree == "Bachelor of Technology"
    assert edu.start_date == "2020"
    assert edu.end_date == "2024"
