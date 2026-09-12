# ResumeIQ — Automated Resume Analyzer

ResumeIQ is a robust, local-first Automated Resume Analyzer built with Python and FastAPI. It extracts structured data (Contact Information, Experience, Education, Projects, and Skills) from unstructured PDF and DOCX resumes using a combination of heuristic segmentation, Named Entity Recognition (NER), and a curated Skill Ontology engine.

## Features

- **Multi-format Support:** Parses both `.pdf` and `.docx` files natively.
- **Intelligent Segmentation:** Breaks resumes down into structured canonical sections regardless of formatting.
- **Skill Extraction Engine:** Utilizes an external JSON ontology to extract skills, resolve aliases (e.g. `React.js` -> `React`), and track exact matched evidence.
- **Privacy-First:** Processes everything locally. Uploaded files are handled securely via temporary file buffers and are destroyed immediately after processing.
- **REST API:** FastAPI powered JSON endpoints.
- **Web UI:** A clean, professional web interface for interacting with the parser.
- **Zero Paid Dependencies:** Runs entirely on free, open-source libraries without relying on OpenAI or other paid APIs.

## Architecture

```text
    User / Web UI
          │
          ▼
   POST /api/v1/parse (FastAPI)
          │
          ▼
    ResumeParser (Orchestrator)
          │
          ├── Ingestion (PDFLoader / DOCXLoader)
          │
          ├── Preprocessing (Whitespace, bullets, encoding)
          │
          ├── Section Segmentation (Heuristic mapping to standard headers)
          │
          ├── Information Extraction (Regex + spaCy NER with fallback)
          │
          └── Skill Intelligence (Regex multi-pattern ontology matcher)
          │
          ▼
   Structured JSON Response (Pydantic validated)
```

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic
- **Extraction:** pdfminer.six (PDF), python-docx (DOCX)
- **NLP:** spaCy (`en_core_web_sm`), Regex (re)
- **Frontend:** Vanilla HTML/CSS/JS (served via FastAPI StaticFiles)
- **Testing:** pytest, httpx

## NLP Pipeline & Skill Ontology

ResumeIQ doesn't rely on simplistic keyword matching. The NLP pipeline uses:
- **Heuristics & Regex:** Safely extracts emails, phones, and URLs.
- **Named Entity Recognition (NER):** Uses spaCy to isolate `PERSON` (Candidate Name) and `ORG` (Universities, Companies). Includes a pure-Python fallback algorithm for environments where C-compiled DLLs (like spaCy/lxml) are blocked by system policies.
- **Skill Ontology:** An external JSON knowledge base (`data/ontology/skills.json`) acts as the source of truth for technical and soft skills. The `SkillExtractor` compiles these into boundary-safe regular expressions to prevent false positives (e.g. "C" won't match inside "Cat" or "C++"), resolving aliases ("Python 3") back to canonical forms ("Python").

## Installation

_This guide is optimized for Windows development environments._

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/kashish09121/resume-iq.git
   cd resume-iq
   ```

2. **Create a virtual environment and activate it:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install the NLP Model (Optional but Recommended):**
   ```powershell
   python -m spacy download en_core_web_sm
   ```
   _Note: If spaCy fails to load due to strict execution policies, the system automatically falls back to heuristic extraction without crashing._

## Usage

### Start the Application

Run the application using Uvicorn:

```powershell
uvicorn resume_iq.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### Access the UI
Open your browser and navigate to: **http://127.0.0.1:8000**

### API Endpoints

- `GET /api/v1/health` - Health check.
- `POST /api/v1/parse` - Upload a resume (`multipart/form-data` with `file` key). Returns a highly structured JSON representation of the resume.
- `GET /docs` - Interactive Swagger API documentation.

## Testing

ResumeIQ is fully tested across all modules.

To run the complete test suite (Unit + Integration):
```powershell
pytest tests/
```

## Privacy & Security

- **Temporary Processing:** Uploads are streamed to a short-lived temporary file created via `tempfile.mkstemp`, which is deleted in a `finally` block before the HTTP request returns.
- **Local First:** No data ever leaves the host machine.
- **Size Limits:** Uploads are capped at 10MB to prevent memory exhaustion attacks.
- **File Validation:** Strictly validates file extensions and sizes before loading.

## Limitations

- Currently cannot OCR scanned image-based PDFs.
- Highly unusual or visually complex multi-column layouts may occasionally confuse the heuristic segmenter.
- The Skill Matcher only detects skills listed in the `skills.json` ontology. Novel skills not present in the JSON will not be extracted.

## License

Copyright (c) 2026 Kashish. Licensed under the [MIT License](LICENSE).
