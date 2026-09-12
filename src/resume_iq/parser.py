from resume_iq.ingestion.loaders import DocumentLoaderFactory
from resume_iq.ingestion.models import PreprocessedDocument

class ResumeParser:
    """Orchestrator for the ResumeIQ parsing pipeline."""
    
    def __init__(self):
        # Initialization for segmenters, extractors, etc. will go here.
        pass
        
    def parse(self, filepath: str) -> dict:
        """Full parsing pipeline: ingestion -> segmentation -> extraction -> validation."""
        # 1. Ingestion and Preprocessing
        doc = self._ingest(filepath)
        
        # 2. Section Segmentation (Planned for Next Milestone)
        # 3. Information Extraction (Planned)
        # 4. Data Validation and Structuring (Planned)
        
        # For this milestone, we simply return the preprocessed document representation
        # to prove the ingestion layer works.
        return {
            "source": doc.source_name,
            "type": doc.source_type,
            "lines": doc.lines,
            "status": "ingested"
        }

    def _ingest(self, filepath: str) -> PreprocessedDocument:
        """Load and preprocess the document."""
        loader = DocumentLoaderFactory.get_loader(filepath)
        return loader.load()

def parsefile(filepath: str) -> dict:
    """Convenience function to parse a resume file."""
    parser = ResumeParser()
    return parser.parse(filepath)
