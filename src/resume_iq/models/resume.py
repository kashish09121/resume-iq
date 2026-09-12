from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Contact(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Experience(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class SkillEvidence(BaseModel):
    matched_alias: str
    source_section: str
    evidence_text: str
    match_method: str
    
class Skill(BaseModel):
    canonical_name: str
    category: Optional[str] = None
    skill_type: Optional[str] = None
    aliases_matched: List[str] = Field(default_factory=list)
    evidence: List[SkillEvidence] = Field(default_factory=list)

class Resume(BaseModel):
    contact: Contact = Field(default_factory=Contact)
    summary: Optional[str] = None
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
