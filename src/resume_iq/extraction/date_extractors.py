import re
from typing import Optional, Tuple

class DateExtractor:
    """Extracts date strings and ranges from text."""
    
    # Months spelled out, abbreviated, or 2 digits
    MONTHS = r'(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|(?:0?[1-9]|1[0-2]))'
    # Year (usually 4 digits starting with 19 or 20)
    YEAR = r'(?:19|20)\d{2}'
    
    # E.g., Jan 2024, 01/2024, 2024
    SINGLE_DATE_PATTERN = re.compile(rf'\b(?:{MONTHS}[-/\s]*)?{YEAR}\b', re.IGNORECASE)
    
    # E.g., Present, Current
    PRESENT_PATTERN = re.compile(r'\b(?:present|current|now|till date)\b', re.IGNORECASE)

    @classmethod
    def extract_date_range(cls, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts start and end dates from a string.
        Returns (start_date, end_date) where end_date might be "Present".
        """
        # Find all absolute dates in the string
        dates = cls.SINGLE_DATE_PATTERN.findall(text)
        
        if not dates:
            return None, None
            
        start_date = dates[0]
        end_date = None
        
        if len(dates) > 1:
            end_date = dates[-1] # Usually start ... end
        elif cls.PRESENT_PATTERN.search(text):
            end_date = "Present"
            
        return start_date, end_date
