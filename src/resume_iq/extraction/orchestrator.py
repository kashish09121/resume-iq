import re
from typing import List, Optional, Dict, Any
from resume_iq.models.resume import Resume, Contact, Experience, Education
from resume_iq.segmentation.models import StructuredResume, Section
from resume_iq.extraction.regex_extractors import RegexExtractor
from resume_iq.extraction.ner_extractors import NERExtractor
from resume_iq.extraction.date_extractors import DateExtractor

class InformationExtractor:
    """Orchestrates Regex, NER, and Contextual heuristics to populate the Data Model."""
    
    # Common degree normalizations
    DEGREE_ALIASES = {
        "btech": "Bachelor of Technology",
        "b.tech": "Bachelor of Technology",
        "b.tech.": "Bachelor of Technology",
        "bachelor of technology": "Bachelor of Technology",
        "b.e.": "Bachelor of Engineering",
        "be": "Bachelor of Engineering",
        "bsc": "Bachelor of Science",
        "b.sc": "Bachelor of Science",
        "mtech": "Master of Technology",
        "m.tech": "Master of Technology",
        "mba": "Master of Business Administration",
        "bca": "Bachelor of Computer Applications",
        "phd": "Doctor of Philosophy",
        "ph.d": "Doctor of Philosophy",
    }
    
    # Common degree patterns
    DEGREE_PATTERN = re.compile(r'\b(?:b\.?tech|b\.?e\.?|b\.?s\.?c|m\.?tech|m\.?b\.?a\.?|ph\.?d\.?|bca|bachelor|master|doctorate)\b', re.IGNORECASE)

    def extract(self, structured: StructuredResume) -> Resume:
        resume = Resume()
        
        # 1. Extract Contact Information
        resume.contact = self._extract_contact(structured.contact)
        
        # 2. Extract Summary
        if "summary" in structured.sections and structured.sections["summary"]:
            # Join lines of the first summary section found
            resume.summary = "\n".join(structured.sections["summary"][0].lines)
            
        # 3. Extract Experience
        if "experience" in structured.sections:
            for exp_section in structured.sections["experience"]:
                # If there are multiple experience blocks (e.g. grouped by job),
                # we parse each block into one or more Experience objects.
                # A simple heuristic: each blank-line-separated chunk in the block
                # might be a separate job, but since cleaner collapsed them, we just 
                # extract what we can heuristically.
                exp = self._parse_experience_block(exp_section.lines)
                resume.experience.extend(exp)
                
        # 4. Extract Education
        if "education" in structured.sections:
            for edu_section in structured.sections["education"]:
                edu = self._parse_education_block(edu_section.lines)
                resume.education.extend(edu)
                
        # 5. Extract Projects (Basic assignment for this milestone)
        if "projects" in structured.sections:
            for proj_section in structured.sections["projects"]:
                resume.projects.append("\n".join(proj_section.lines))

        # 6. Extract Skills across sections
        from resume_iq.extraction.skill_extractor import SkillExtractor
        skill_extractor = SkillExtractor()
        
        # Merge dictionary mapping canonical_name -> Skill object
        all_skills = {}
        
        # 6a. Explicit skills section
        if "skills" in structured.sections:
            for skill_sec in structured.sections["skills"]:
                text = "\n".join(skill_sec.lines)
                extracted = skill_extractor.extract_from_text(text, "skills")
                self._merge_skills(all_skills, extracted)
                
        # 6b. Experience sections
        if "experience" in structured.sections:
            for exp_sec in structured.sections["experience"]:
                text = "\n".join(exp_sec.lines)
                extracted = skill_extractor.extract_from_text(text, "experience")
                self._merge_skills(all_skills, extracted)
                
        # 6c. Project sections
        if "projects" in structured.sections:
            for proj_sec in structured.sections["projects"]:
                text = "\n".join(proj_sec.lines)
                extracted = skill_extractor.extract_from_text(text, "projects")
                self._merge_skills(all_skills, extracted)
                
        resume.skills = list(all_skills.values())

        # Store metadata about extraction
        resume.metadata["extraction_methods_used"] = ["Regex", "spaCy NER", "Heuristic", "Ontology"]
        
        return resume

    def _merge_skills(self, all_skills: Dict[str, Any], new_skills: List[Any]):
        """Merges new extracted skills into the tracking dictionary to deduplicate globally."""
        for skill in new_skills:
            if skill.canonical_name not in all_skills:
                all_skills[skill.canonical_name] = skill
            else:
                existing = all_skills[skill.canonical_name]
                for alias in skill.aliases_matched:
                    if alias not in existing.aliases_matched:
                        existing.aliases_matched.append(alias)
                existing.evidence.extend(skill.evidence)

    def _extract_contact(self, contact_section: Section) -> Contact:
        text = "\n".join(contact_section.lines)
        contact = Contact()
        
        contact.email = RegexExtractor.extract_email(text)
        contact.phone = RegexExtractor.extract_phone(text)
        contact.linkedin = RegexExtractor.extract_linkedin(text)
        contact.portfolio = RegexExtractor.extract_portfolio(text)
        
        # Candidate Name uses contextual NER
        contact.name = NERExtractor.extract_candidate_name(contact_section.lines, contact.email)
        
        return contact

    def _parse_experience_block(self, lines: List[str]) -> List[Experience]:
        """Contextually extract experience details."""
        if not lines:
            return []
            
        # For simplicity in this milestone, we treat the entire section lines as one job.
        # A more advanced chunker would split by dates. We will extract the *first* date range
        # and *first* ORG.
        exp = Experience()
        
        text = "\n".join(lines)
        entities = NERExtractor.extract_entities(text)
        
        if "ORG" in entities and entities["ORG"]:
            exp.company = entities["ORG"][0]  # Take the first organization
            
        # Find dates
        for line in lines:
            start, end = DateExtractor.extract_date_range(line)
            if start:
                exp.start_date = start
                exp.end_date = end
                exp.dates = line.strip()
                break
                
        # Assume job title might be in the first 2 lines
        # If it doesn't have the date and isn't the ORG, it might be the title
        for i in range(min(3, len(lines))):
            line = lines[i].strip()
            if not line: continue
            
            # Simple heuristic
            if exp.company and exp.company in line:
                continue
            if exp.start_date and exp.start_date in line:
                continue
            if len(line) > 50: # too long for title
                continue
                
            # It's a decent candidate for a job title
            exp.job_title = line
            break
            
        exp.description = text
        return [exp]

    def _parse_education_block(self, lines: List[str]) -> List[Education]:
        """Contextually extract education details."""
        if not lines:
            return []
            
        edu = Education()
        text = "\n".join(lines)
        
        # Extract Institution via NER
        entities = NERExtractor.extract_entities(text)
        if "UNIVERSITY" in entities and entities["UNIVERSITY"]:
            edu.institution = entities["UNIVERSITY"][0]
        elif "ORG" in entities and entities["ORG"]:
            # Universities are usually ORGs
            edu.institution = entities["ORG"][0]
            
        # Extract Dates
        for line in lines:
            start, end = DateExtractor.extract_date_range(line)
            if start:
                edu.start_date = start
                edu.end_date = end
                break
                
        # Extract Degree
        if "DEGREE" in entities and entities["DEGREE"]:
            edu.degree = entities["DEGREE"][0]
            # Try to get field heuristically
            for line in lines:
                if edu.degree in line:
                    edu.field = line.strip()
                    break
        else:
            for line in lines:
                match = self.DEGREE_PATTERN.search(line)
                if match:
                    raw_deg = match.group(0)
                    clean_deg = re.sub(r'[^a-z0-9]', '', raw_deg.lower())
                    
                    # Try normalization
                    edu.degree = self.DEGREE_ALIASES.get(clean_deg, raw_deg)
                    
                    # The whole line might be the field (e.g. B.Tech in Computer Science)
                    edu.field = line.strip()
                    break
                
        return [edu]
