import re
from typing import List, Dict, Optional

# Attempt to load spaCy, but provide a pure Python fallback if 
# Windows Application Control / AppLocker blocks the C-extension DLLs.
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class NLPModelLoader:
    """Singleton to load the spaCy model efficiently once per lifecycle."""
    _model = None

    @classmethod
    def get_model(cls):
        if not SPACY_AVAILABLE:
            return None
        if cls._model is None:
            try:
                cls._model = spacy.load("en_core_web_sm")
            except OSError:
                return None # Model not downloaded
        return cls._model

class NERExtractor:
    """Semantic extraction using spaCy NER, with a heuristic fallback."""

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, List[str]]:
        """Extract all entities from a block of text, grouped by label."""
        nlp = NLPModelLoader.get_model()
        entities = {}
        
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                clean_text = " ".join(ent.text.split())
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                if clean_text not in entities[ent.label_]:
                    entities[ent.label_].append(clean_text)
            return entities
            
        # --- PURE PYTHON HEURISTIC FALLBACK (For AppLocker environments) ---
        # Heuristic ORG: Capitalized words followed by University, College, Inc, Corp, LLC, etc.
        org_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|College|Institute|School|Inc\.?|Corp\.?|LLC|Ltd\.?|Technologies|Solutions))(?:\b|\Z)')
        orgs = org_pattern.findall(text)
        if orgs:
            entities["ORG"] = orgs
            
        return entities

    @classmethod
    def extract_candidate_name(cls, contact_lines: List[str], email: Optional[str] = None) -> Optional[str]:
        """Robustly extracts the candidate name from contact section lines."""
        nlp = NLPModelLoader.get_model()
        
        for line in contact_lines:
            persons = []
            if nlp:
                doc = nlp(line)
                persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            else:
                # Heuristic PERSON fallback: 2-3 capitalized words in a short line
                words = line.strip().split()
                if 1 < len(words) <= 3 and all(w.istitle() for w in words) and len(line) < 30:
                    persons = [line.strip()]
            
            if persons:
                name = persons[0]
                if email:
                    email_prefix = email.split('@')[0].lower()
                    name_parts = name.lower().split()
                    if any(part in email_prefix for part in name_parts):
                        return name
                else:
                    return name
        
        # Fallback: The very first line of the resume
        if contact_lines:
            first_line = contact_lines[0].strip()
            if 1 < len(first_line.split()) <= 4 and len(first_line) < 30:
                return first_line
                
        return None
