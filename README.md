# ResumeIQ — Automated Resume Analyzer

ResumeIQ is a robust, local-first, privacy-focused automated resume analyzer. It extracts structured information (Candidate Details, Experience, Education, Projects, and Skills) from unstructured PDF and DOCX resumes without relying on external APIs or cloud models.

## 🎯 Key Features

- **Local-First Processing:** No data leaves your machine. Perfect for privacy-sensitive documents.
- **Dependency-Light:** Uses pure Python libraries (`pdfminer.six`, `python-docx`) to avoid C-extension/DLL restrictions (e.g., Windows AppLocker).
- **Robust NLP & Heuristics:** Employs a custom semantic segmentation engine to map lines to canonical sections, avoiding the "giant paragraph" problem common in basic parsers.
- **Intelligent Skill Extraction:** Uses an alias-aware, regex-compiled Skill Ontology to safely extract skills while preserving punctuation (e.g., C++, .NET) and deduplicating matches across sections.
- **API First:** Built on FastAPI, ready for integration.
- **Vanilla UI:** A clean, zero-build-step HTML/JS/CSS frontend for instant demonstration.

## 🏗️ Architecture Recap

The system follows a strict pipeline architecture, ensuring modularity and testability at every stage:

1. **Ingestion (`src/resume_iq/ingestion`):** Loads PDF/DOCX files natively into memory and extracts raw text while preserving line structure.
2. **Preprocessing (`src/resume_iq/preprocessing`):** Normalizes Unicode, strips erratic whitespace, and outputs a `PreprocessedDocument`.
3. **Segmentation (`src/resume_iq/segmentation`):** Analyzes heading structures using deterministic heuristics (uppercase, short length, synonym matching) to group lines into semantic `Sections` (Contact, Experience, Education, etc.).
4. **Information Extraction (`src/resume_iq/extraction`):** 
   - Uses a trained/fine-tuned custom spaCy NER model to detect `CANDIDATE_NAME`, `UNIVERSITY`, and `DEGREE`. (If the custom model is missing, falls back to `en_core_web_sm` and heuristics).
   - Phone numbers are normalized to a canonical international E.164 representation using the `phonenumbers` library (defaults to the `IN` region for ambiguous numbers).
   - Dynamically parses the `skills.json` ontology to find skills across all sections, recording the exact canonical match and the evidence.
5. **Data Models (`src/resume_iq/models`):** Heavily relies on Pydantic `Resume` models for rigorous type validation and serialization. The `Experience` model preserves the original `dates` representation while still providing structured `start_date` and `end_date`.
6. **API Layer (`src/resume_iq/api`):** Exposes a secure FastAPI endpoint (`/api/v1/parse`) handling CORS, size limits, and robust temp file management. The parser API can also be used programmatically via `ResumeParser().parsefile(filepath)`.

## 🚀 Quickstart & Local Testing

### 1. Backend Setup

Ensure you have Python 3.10+ installed.

```bash
# Clone the repository
git clone https://github.com/kashish09121/resume-iq.git
cd resume-iq

# Create and activate a virtual environment
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn resume_iq.api.main:app --reload
```

The API will now be running at `http://127.0.0.1:8000`. You can access the Swagger documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

Since the frontend is built with Vanilla HTML/JS/CSS, no build step is required!

1. Open a new terminal.
2. Navigate to the `ui` directory:
   ```bash
   cd ui
   ```
3. Serve the directory using Python's built-in HTTP server:
   ```bash
   python -m http.server 8080
   ```
4. Open your browser and go to `http://localhost:8080`.
5. Upload a PDF or DOCX file to see the parser in action!

## 🧪 Testing

ResumeIQ comes with a comprehensive test suite covering unit tests for all internal modules and adversarial integration tests.

```bash
# Run the test suite
pytest tests/ -v
```

## 🧠 Custom NER Training

ResumeIQ includes a custom spaCy training pipeline for domain-specific entity recognition. To train the model yourself:

1. Ensure your virtual environment is active.
2. Run the training script:
   ```bash
   python training/train_ner.py
   ```
3. The script will train the model using synthetic data (`training/data/train_data.json`) and save it to `models/custom_ner`.
4. The extraction pipeline will automatically detect and prioritize this custom model for enhanced extraction.

## 🔐 Security & Privacy Addendum

ResumeIQ is designed with security and privacy as first-class citizens:

- **Zero Data Egress:** Analysis happens 100% locally. No resume data is sent to external APIs.
- **Strict File Validation:** The FastAPI backend strictly enforces file types (`.pdf`, `.docx`) and caps upload sizes at 5MB to prevent memory exhaustion (DoS).
- **Secure File Handling:** Uploaded files are streamed to secure temporary files using `tempfile.mkstemp()`, mitigating path traversal attacks, and are guaranteed to be cleaned up after processing via `finally` blocks.
- **Dependency Safety:** Favoring pure-Python parsers avoids the severe security vulnerabilities and execution restrictions often associated with native C-extensions in enterprise environments.

## 📜 License

MIT License - Created by [Kashish](https://github.com/kashish09121)
