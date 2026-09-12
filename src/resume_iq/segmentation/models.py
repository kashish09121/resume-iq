from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Section(BaseModel):
    """Represents a logical section within a resume."""
    canonical_name: str
    original_heading: Optional[str]
    lines: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StructuredResume(BaseModel):
    """Structured representation of a resume after segmentation."""
    contact: Section = Field(default_factory=lambda: Section(canonical_name="contact", original_heading=None))
    sections: Dict[str, List[Section]] = Field(default_factory=dict)
    
    def add_section(self, section: Section):
        if section.canonical_name not in self.sections:
            self.sections[section.canonical_name] = []
        self.sections[section.canonical_name].append(section)
