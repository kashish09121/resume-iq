import os
import tempfile
import time
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from resume_iq.parser import ResumeParser
from resume_iq.models.resume import Resume

# Configuration
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app = FastAPI(
    title="ResumeIQ API",
    description="Automated Resume Analyzer API",
    version="1.0.0"
)

# Allow CORS for UI access (configurable for prod, permissive for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Health Check")
async def health_check():
    return {"status": "ok"}

@app.post("/api/v1/parse", response_model=Resume, summary="Parse a resume file (PDF or DOCX)")
async def parse_resume(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")

    # Extension validation
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file format '{ext}'. Please upload a PDF or DOCX resume."
        )

    # Size validation (read into memory, verify, then write to temp)
    file_content = await file.read()
    if len(file_content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_UPLOAD_SIZE_MB}MB."
        )
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Secure temporary file handling
    fd, temp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(file_content)
        
        start_time = time.time()
        
        # Orchestrate processing
        parser = ResumeParser()
        try:
            resume: Resume = parser.parse(temp_path)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            # Internal processing error
            raise HTTPException(status_code=500, detail="The resume could not be processed.")
            
        process_time = time.time() - start_time
        
        # Embed metadata
        resume.metadata["processing_time_ms"] = int(process_time * 1000)
        resume.metadata["source_type"] = ext.lstrip(".")
        
        return resume
        
    finally:
        # Guarantee cleanup for privacy and disk space
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
