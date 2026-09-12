import pytest
import io
from fastapi.testclient import TestClient
from resume_iq.api.main import app
from resume_iq.models.resume import Resume

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_parse_missing_file():
    # Sending without file
    response = client.post("/api/v1/parse")
    assert response.status_code == 422 # FastAPI validation error for missing field

def test_parse_unsupported_format():
    # Send a .txt file
    file_content = b"Some fake resume content"
    files = {"file": ("resume.txt", file_content, "text/plain")}
    response = client.post("/api/v1/parse", files=files)
    
    assert response.status_code == 415
    assert "Unsupported file format" in response.json()["detail"]

def test_parse_empty_file():
    # Send an empty PDF
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    response = client.post("/api/v1/parse", files=files)
    
    assert response.status_code == 400
    assert "Empty file uploaded" in response.json()["detail"]

def test_parse_large_file():
    # Create a 6MB dummy file
    large_content = b"0" * (6 * 1024 * 1024)
    files = {"file": ("large.pdf", large_content, "application/pdf")}
    response = client.post("/api/v1/parse", files=files)
    
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

# For testing a valid file, we need a valid PDF. 
# We'll create a minimal PDF generator for the test or just use a mock if PDF parsing is hard without a real file.
# We will use the DocumentLoaderFactory integration to mock or we can just skip it here and rely on unit tests,
# but end-to-end integration is requested. Since we don't have a reliable way to generate a binary PDF easily in memory
# that pdfminer won't crash on, we'll patch the ResumeParser to return a dummy Resume for the integration test.

from unittest.mock import patch
@patch("resume_iq.api.main.ResumeParser.parse")
def test_parse_valid_file_integration(mock_parse):
    # Setup mock to return a valid Resume object
    mock_resume = Resume()
    mock_resume.contact.name = "Test User"
    mock_resume.metadata["test"] = "true"
    mock_parse.return_value = mock_resume
    
    # We send a "valid" looking file (but the parser is mocked anyway)
    files = {"file": ("resume.pdf", b"fake pdf content", "application/pdf")}
    response = client.post("/api/v1/parse", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["contact"]["name"] == "Test User"
    assert data["metadata"]["test"] == "true"
    assert "processing_time_ms" in data["metadata"]
    assert data["metadata"]["source_type"] == "pdf"
