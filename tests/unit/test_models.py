import pytest
from pydantic import ValidationError
from resume_iq.models.resume import Resume, Contact, Experience

def test_resume_model_instantiation():
    """Test that a Resume model can be instantiated with default/empty fields."""
    resume = Resume()
    assert resume.contact is not None
    assert isinstance(resume.skills, list)
    assert len(resume.skills) == 0
    assert resume.summary is None

def test_resume_model_validation():
    """Test that valid nested data works correctly."""
    contact_data = {"name": "Alice Smith", "email": "alice@example.com"}
    exp_data = {"company": "Tech Corp", "job_title": "Engineer"}
    
    resume = Resume(
        contact=Contact(**contact_data),
        experience=[Experience(**exp_data)],
        skills=["Python", "FastAPI"]
    )
    
    assert resume.contact.name == "Alice Smith"
    assert resume.experience[0].company == "Tech Corp"
    assert "Python" in resume.skills
