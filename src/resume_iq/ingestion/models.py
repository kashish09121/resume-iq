from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PreprocessedDocument(BaseModel):
    """Internal representation of a document after extraction and cleaning."""
    source_name: str
    source_type: str  # e.g., 'pdf', 'docx'
    raw_text: str = ""
    clean_text: str = ""
    lines: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
