import os
import shutil
import tempfile
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from resume_iq.parser import ResumeParser
from resume_iq.models.resume import Resume

# Configuration
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app = FastAPI(
    title="ResumeIQ API",
    description="Automated Resume Analyzer Backend API",
    version="1.0.0"
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configurable in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/v1/parse", response_model=Resume)
async def parse_resume(file: UploadFile = File(...)):
    start_time = time.time()
    
    # Validation 1: Check filename and extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
    # Validation 2: Check file size by reading chunk
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB.")
        
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
    # Create temporary file safely
    temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
    os.close(temp_fd) # Close it so we can open it via shutil
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Orchestrate the parser
        parser = ResumeParser()
        try:
            resume_dict = parser.parse(temp_path)
            # Parse dict back into Resume model for validation and metadata appending
            resume = Resume(**resume_dict)
            
            # Add API-level metadata
            processing_time = round(time.time() - start_time, 2)
            resume.metadata["processing_time_sec"] = processing_time
            resume.metadata["source_type"] = ext.replace(".", "")
            
            return resume
            
        except ValueError as ve:
            # Handle known parser errors (like no text extracted)
            raise HTTPException(status_code=422, detail=str(ve))
        except Exception as e:
            # Catch-all for unexpected parser crashes
            raise HTTPException(status_code=500, detail="An error occurred while processing the resume.")
            
    finally:
        # Cleanup temporary file reliably
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass # Silent cleanup failure

# Mount frontend static files
# Ensure the 'static' directory exists before mounting to avoid startup errors
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
