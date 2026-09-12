# ResumeIQ — Automated Resume Analyzer

A modular, local-first automated resume analysis system capable of parsing PDF and DOCX files, extracting raw text, segmenting logical sections, and extracting structured information such as entities, skills, and contact details.

## Current Development Status
- **Foundation / Environment**: Implemented
- **Data Models**: Implemented
- **Configuration**: Implemented
- **Document Ingestion (PDF/DOCX)**: Planned
- **Text Normalization**: Planned
- **Section Segmentation**: Planned
- **Information Extraction (NER, Regex)**: Planned
- **Skill Matching**: Planned
- **API Wrapper**: Planned
- **Web UI**: Planned

## Core Architecture
ResumeIQ uses a pipelined approach to analyze resumes:
1. **Document Loader**: Extracts raw text locally (using `pdfminer.six` and `python-docx`).
2. **Cleaner & Segmenter**: Prepares and chunks the text into logical blocks (e.g. Experience, Education).
3. **Extractors**: Regex, spaCy NER, and an external skill ontology are used to extract entities.
4. **Normalizer & Validator**: Normalizes extracted data and validates it via Pydantic models.
5. **Output**: Exposes the parsed data as structured JSON.

## Technology Stack
- **Language:** Python 3.10+
- **Parsing:** `pdfminer.six`, `python-docx`
- **NLP / ML:** `spaCy`
- **Data Validation:** `Pydantic`
- **API Backend:** `FastAPI`
- **Testing:** `pytest`

## Windows Setup & Installation

ResumeIQ is designed to be fully runnable on a Windows machine.

### 1. Create a Virtual Environment (PowerShell)
```powershell
# Create the environment
python -m venv .venv

# Activate the environment
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
# Install project in editable mode with development dependencies
pip install -e ".[dev]"
```

### 3. NLP Model Management (spaCy)
ResumeIQ currently uses the `en_core_web_sm` model. You must download it before running the extractors:
```powershell
python -m spacy download en_core_web_sm
```

### 4. Run Tests
Verify your installation by running the foundation test suite:
```powershell
pytest
```

## Privacy & Security
- **Local-first**: The parsing engine runs entirely on your local hardware. No resumes are sent to third-party APIs or cloud services.
- **Data Retention**: By design, temporary files are used during upload/parsing and are immediately deleted. No PII is logged.

## License
Copyright (c) 2026 Kashish. Licensed under the MIT License.
