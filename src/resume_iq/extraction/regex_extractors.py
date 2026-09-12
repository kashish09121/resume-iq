import re
from typing import Optional, Tuple

class RegexExtractor:
    """Robust regex-based extraction for highly structured fields."""
    
    # Common email pattern, handles + tags and standard TLDs
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    
    # Phone pattern: supports optional country code, dashes, parentheses, spaces
    PHONE_PATTERN = re.compile(r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4})')
    
    # LinkedIn pattern
    LINKEDIN_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+')
    
    # Generic URL pattern (naive, filtering for common portfolio hosting)
    URL_PATTERN = re.compile(r'(?:https?://)?(?:www\.)?(github\.com/[a-zA-Z0-9_-]+|[a-zA-Z0-9_-]+\.(?:com|org|net|me|io)(?:/[a-zA-Z0-9_-]+)?)')

    @classmethod
    def extract_email(cls, text: str) -> Optional[str]:
        match = cls.EMAIL_PATTERN.search(text)
        if match:
            return match.group(0).lower()
        return None

    @classmethod
    def extract_phone(cls, text: str) -> Optional[str]:
        # Since the generic phone regex can match arbitrary numbers (like zip codes or IDs),
        # we enforce length and structure heuristics on the matched string.
        matches = cls.PHONE_PATTERN.findall(text)
        for match in matches:
            # Strip non-digits to check core length
            digits = re.sub(r'\D', '', match)
            if 10 <= len(digits) <= 15:
                # Basic validation: normal phone numbers are 10-15 digits
                return match.strip()
        return None

    @classmethod
    def extract_linkedin(cls, text: str) -> Optional[str]:
        match = cls.LINKEDIN_PATTERN.search(text)
        if match:
            url = match.group(0)
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return None

    @classmethod
    def extract_portfolio(cls, text: str) -> Optional[str]:
        # A portfolio is a URL that isn't LinkedIn
        linkedin = cls.extract_linkedin(text)
        matches = cls.URL_PATTERN.findall(text)
        
        for match in matches:
            # Avoid picking up default string artifacts if not careful, reconstruct URL
            if linkedin and match in linkedin:
                continue
                
            # If the regex returned a tuple or sub-group, handle it correctly:
            url = match if isinstance(match, str) else match[0]
            
            if 'linkedin.com' not in url.lower():
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        return None
