import re
from typing import List

class TextCleaner:
    """Modular pipeline for cleaning and normalizing extracted resume text."""

    # Bullet points that need normalization
    BULLET_CHARS = [r'•', r'●', r'○', r'▪', r'–', r'—', r'\*', r'·', r'-']
    BULLET_PATTERN = re.compile(r'^[\s]*(' + '|'.join(BULLET_CHARS) + r')\s+')

    @classmethod
    def clean(cls, raw_text: str) -> str:
        """Apply the full cleaning pipeline to raw text."""
        lines = raw_text.splitlines()
        
        # 1. Normalize line endings and whitespace
        lines = cls._normalize_whitespace(lines)
        
        # 2. Normalize bullets
        lines = cls._normalize_bullets(lines)
        
        # 3. Handle special chars/artifacts
        lines = cls._handle_special_characters(lines)
        
        # 4. Remove noise (repeated headers/footers)
        lines = cls._reduce_noise(lines)
        
        # 5. Remove excessive empty lines
        lines = cls._clean_empty_lines(lines)

        return '\n'.join(lines)

    @staticmethod
    def _normalize_whitespace(lines: List[str]) -> List[str]:
        """Convert tabs to spaces and reduce repeated spaces."""
        cleaned = []
        for line in lines:
            # Replace tabs with spaces
            line = line.replace('\t', ' ')
            # Reduce multiple spaces to single space
            line = re.sub(r' {2,}', ' ', line)
            # Strip trailing/leading whitespace
            cleaned.append(line.strip())
        return cleaned

    @classmethod
    def _normalize_bullets(cls, lines: List[str]) -> List[str]:
        """Normalize varied bullet characters to a standard representation '• '."""
        cleaned = []
        for line in lines:
            line = cls.BULLET_PATTERN.sub('• ', line)
            cleaned.append(line)
        return cleaned

    @staticmethod
    def _handle_special_characters(lines: List[str]) -> List[str]:
        """Remove control characters but keep safe unicode symbols."""
        cleaned = []
        for line in lines:
            # Remove unprintable control characters except standard whitespace
            # Uses a generator expression to filter chars
            line = ''.join(ch for ch in line if ch.isprintable() or ch.isspace())
            cleaned.append(line)
        return cleaned

    @staticmethod
    def _reduce_noise(lines: List[str]) -> List[str]:
        """Heuristically remove page numbers or repeated headers."""
        cleaned = []
        page_num_pattern = re.compile(r'^(page\s*\d+(\s*of\s*\d+)?|\d+\s*\|\s*page)$', re.IGNORECASE)
        for line in lines:
            if page_num_pattern.match(line):
                continue
            # Note: More advanced duplicate header detection could go here if needed.
            # For now, we rely on page number reduction.
            cleaned.append(line)
        return cleaned

    @staticmethod
    def _clean_empty_lines(lines: List[str]) -> List[str]:
        """Remove consecutive empty lines, reducing them to at most one."""
        cleaned = []
        prev_empty = False
        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            cleaned.append(line)
            prev_empty = is_empty
            
        # Ensure we don't start or end with empty lines
        if cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        if cleaned and not cleaned[-1].strip():
            cleaned.pop()
            
        return cleaned
