from resume_iq.ingestion.loaders import DocumentLoaderFactory
from resume_iq.ingestion.models import PreprocessedDocument
from resume_iq.segmentation.segmenter import SectionSegmenter
from resume_iq.extraction.orchestrator import InformationExtractor

class ResumeParser:
    """Orchestrator for the ResumeIQ parsing pipeline."""
    
    def __init__(self):
        # Initialization for segmenters, extractors, etc. will go here.
        pass
        
    def parse(self, filepath: str) -> dict:
        """Full parsing pipeline: ingestion -> segmentation -> extraction -> validation."""
        # 1. Ingestion and Preprocessing
        doc = self._ingest(filepath)
        
        # 2. Section Segmentation
        segmenter = SectionSegmenter()
        structured_resume = segmenter.segment(doc)
        
        # 3. Information Extraction
        extractor = InformationExtractor()
        resume_data = extractor.extract(structured_resume)
        
        # 4. Data Validation and Structuring (Planned)
        
        # Return the final Pydantic model dump
        return resume_data.model_dump()

    def _ingest(self, filepath: str) -> PreprocessedDocument:
        """Load and preprocess the document."""
        loader = DocumentLoaderFactory.get_loader(filepath)
        return loader.load()

def parsefile(filepath: str) -> dict:
    """Convenience function to parse a resume file."""
    parser = ResumeParser()
    return parser.parse(filepath)
