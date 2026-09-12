import pytest
import os
from fastapi.testclient import TestClient
from resume_iq.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_parse_missing_file():
    response = client.post("/api/v1/parse")
    # FastAPI returns 422 Unprocessable Entity when required form data is missing
    assert response.status_code == 422 

def test_parse_unsupported_file():
    # Send a .txt file which is unsupported
    files = {"file": ("test.txt", b"Hello world", "text/plain")}
    response = client.post("/api/v1/parse", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_parse_empty_pdf(tmp_path):
    # Create a 0 byte file
    empty_pdf = tmp_path / "empty.pdf"
    empty_pdf.touch()
    
    with open(empty_pdf, "rb") as f:
        files = {"file": ("empty.pdf", f, "application/pdf")}
        response = client.post("/api/v1/parse", files=files)
        
    assert response.status_code == 400
    assert "Empty file uploaded" in response.json()["detail"]

def test_parse_valid_pdf():
    # Use the sample resume from our tests directory
    sample_pdf = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "samples", "sample.pdf")
    
    # Only run if we actually have the sample pdf available in the tree
    if not os.path.exists(sample_pdf):
        pytest.skip("Sample PDF not found, skipping integration test.")
        
    with open(sample_pdf, "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        response = client.post("/api/v1/parse", files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "contact" in data
    assert "skills" in data
    # Ensure metadata is injected
    assert "processing_time_sec" in data["metadata"]
    assert data["metadata"]["source_type"] == "pdf"
