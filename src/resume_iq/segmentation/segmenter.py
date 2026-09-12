import re
from typing import Tuple, Optional
from resume_iq.ingestion.models import PreprocessedDocument
from resume_iq.segmentation.models import StructuredResume, Section
from resume_iq.segmentation.config import SECTION_ALIASES, OTHER_SECTIONS

class SectionSegmenter:
    """Transforms a cleaned document into structured logical sections."""
    
    def __init__(self):
        self.aliases = SECTION_ALIASES
        self.other_sections = set(OTHER_SECTIONS)
        
    def _normalize_heading(self, line: str) -> str:
        """Strip punctuation and normalize case for matching."""
        clean = line.strip().lower()
        # Remove non-alphanumeric except spaces
        clean = re.sub(r'[^a-z0-9\s]', '', clean).strip()
        # Reduce spaces
        clean = re.sub(r'\s+', ' ', clean)
        return clean

    def _is_heading(self, line: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Determines if a line is a section heading.
        Returns: (is_heading, canonical_name, original_heading_clean)
        """
        norm = self._normalize_heading(line)
        if not norm or len(norm) > 40: # Headings are rarely >40 chars
            return False, None, None
            
        # 1. Check strict known aliases
        for canonical, aliases in self.aliases.items():
            if norm in aliases:
                return True, canonical, norm
                
        # 2. Check other known sections
        if norm in self.other_sections:
            return True, "other", norm

        # 3. Defensive heuristic against false positives:
        # If it doesn't match an alias, we do NOT blindly assume short uppercase lines
        # are headings. e.g. "PYTHON DEVELOPER" or "ABC UNIVERSITY" would be false positives.
        # Strict alias matching is preferred, as new aliases can simply be added to config.
        
        return False, None, None

    def segment(self, doc: PreprocessedDocument) -> StructuredResume:
        """Process lines into structured sections."""
        structured = StructuredResume()
        
        # We start in the contact section
        current_section = structured.contact
        
        for line in doc.lines:
            # Check if this line is a new heading
            is_heading, canonical, norm = self._is_heading(line)
            
            if is_heading:
                # Save the new section and switch to it
                new_section = Section(
                    canonical_name=canonical,
                    original_heading=line.strip(),
                    confidence=1.0,
                    metadata={"normalized_match": norm}
                )
                structured.add_section(new_section)
                current_section = new_section
            else:
                # Append line to the current active section
                current_section.lines.append(line)
                
        # Clean up empty lines from the end of sections
        self._post_process(structured)
        
        return structured

    def _post_process(self, structured: StructuredResume):
        """Trim trailing empty lines from sections."""
        for section in [structured.contact] + [s for sections in structured.sections.values() for s in sections]:
            while section.lines and not section.lines[-1].strip():
                section.lines.pop()
            while section.lines and not section.lines[0].strip():
                section.lines.pop(0)
