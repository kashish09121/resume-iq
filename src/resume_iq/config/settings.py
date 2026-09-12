import os

class Settings:
    """Project configuration settings."""
    
    # Environment
    ENV = os.getenv("RESUMEIQ_ENV", "development")
    LOG_LEVEL = os.getenv("RESUMEIQ_LOG_LEVEL", "INFO")
    
    # File Processing
    MAX_UPLOAD_SIZE_MB = int(os.getenv("RESUMEIQ_MAX_UPLOAD_SIZE_MB", "5"))
    SUPPORTED_EXTENSIONS = [".pdf", ".docx"]
    
    # NLP / ML
    SPACY_MODEL = os.getenv("RESUMEIQ_SPACY_MODEL", "en_core_web_sm")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ONTOLOGY_PATH = os.path.join(BASE_DIR, "data", "ontology", "skills.json")

settings = Settings()
