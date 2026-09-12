import json
import re
from typing import List, Dict, Set
from pathlib import Path
from resume_iq.models.resume import Skill, SkillEvidence

class SkillOntology:
    def __init__(self, filepath: str = "data/ontology/skills.json"):
        self.filepath = filepath
        self.ontology_data = self._load_ontology()
        self.version = self.ontology_data.get("ontology_version", "1.0.0")
        self.skills_list = self.ontology_data.get("skills", [])
        
        self.canonical_map = {}  # alias_lower -> ontology_skill_dict
        self._build_maps()
        
    def _load_ontology(self) -> Dict:
        path = Path(self.filepath)
        if not path.exists():
            # Create an empty one if missing to not crash (e.g., in some test environments)
            return {"ontology_version": "1.0.0", "skills": []}
            
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"Ontology file {self.filepath} is malformed JSON.")

    def _build_maps(self):
        """Validates and builds the alias-to-canonical mapping."""
        for skill in self.skills_list:
            can_name = skill.get("canonical_name")
            if not can_name:
                continue
                
            # Map canonical name
            self._add_to_map(can_name.lower(), skill)
            
            # Map aliases
            for alias in skill.get("aliases", []):
                self._add_to_map(alias.lower(), skill)

    def _add_to_map(self, term: str, skill: Dict):
        # Prevent alias collision (simple validation)
        if term in self.canonical_map:
            existing = self.canonical_map[term]["canonical_name"]
            if existing != skill["canonical_name"]:
                # Log or handle collision - for now, first one wins in a simplistic way,
                # but a real system might throw an error or use context.
                pass
        self.canonical_map[term] = skill


class SkillExtractor:
    def __init__(self, ontology: SkillOntology = None):
        self.ontology = ontology or SkillOntology()
        self._pattern = self._build_regex()

    def _build_regex(self) -> re.Pattern:
        """
        Builds a single highly efficient regex pattern to match all known skills.
        Uses boundary assertions that work safely with punctuation like C++ or .NET
        """
        if not self.ontology.canonical_map:
            # Matches nothing
            return re.compile(r'(?!)')
            
        # Sort terms by length descending to match longest phrase first (e.g., "Python 3" before "Python")
        terms = sorted(self.ontology.canonical_map.keys(), key=len, reverse=True)
        escaped_terms = [re.escape(term) for term in terms]
        
        # We use negative lookbehinds/lookaheads for alphanumeric characters.
        # This acts like a word boundary (\b) but is safe for non-word chars (like ++ or #).
        pattern_str = r'(?<![a-zA-Z0-9])(' + '|'.join(escaped_terms) + r')(?![a-zA-Z0-9])'
        
        return re.compile(pattern_str, re.IGNORECASE)

    def extract_from_text(self, text: str, source_section: str) -> List[Skill]:
        """
        Extracts skills from text and maps them to canonical representation with evidence.
        Returns deduplicated List[Skill].
        """
        if not text:
            return []

        # Find all matches (which are the aliases/canonical names found in text)
        matches = self._pattern.findall(text)
        
        # Deduplicate while merging evidence
        extracted_skills: Dict[str, Skill] = {}
        
        for match in matches:
            match_lower = match.lower()
            onto_skill = self.ontology.canonical_map.get(match_lower)
            if not onto_skill:
                continue
                
            canonical_name = onto_skill["canonical_name"]
            
            # Evidence
            evidence = SkillEvidence(
                matched_alias=match,
                source_section=source_section,
                evidence_text=text[:100],  # Snapshot of context
                match_method="ontology_regex"
            )
            
            if canonical_name not in extracted_skills:
                extracted_skills[canonical_name] = Skill(
                    canonical_name=canonical_name,
                    category=onto_skill.get("category"),
                    skill_type=onto_skill.get("skill_type"),
                    aliases_matched=[match],
                    evidence=[evidence]
                )
            else:
                existing_skill = extracted_skills[canonical_name]
                if match not in existing_skill.aliases_matched:
                    existing_skill.aliases_matched.append(match)
                # Append evidence
                existing_skill.evidence.append(evidence)
                
        return list(extracted_skills.values())
