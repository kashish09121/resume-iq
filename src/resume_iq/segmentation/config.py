# Mapping of canonical section names to their common variations
SECTION_ALIASES = {
    "summary": [
        "summary", "professional summary", "profile", "objective", "career objective", 
        "executive summary", "professional profile", "about me"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment history", 
        "work history", "employment", "project experience", "career history", "experience summary"
    ],
    "education": [
        "education", "academic background", "educational qualifications", "academics", 
        "education and training", "academic profile"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "competencies", "technologies", 
        "expertise", "it skills", "software skills", "technical expertise", "skills summary"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects", "notable projects"
    ]
}

# Common sections that don't have dedicated processing yet, but should be identified as sections
# rather than ignored or grouped under something else.
OTHER_SECTIONS = [
    "certifications", "awards", "publications", "volunteering", "languages", 
    "interests", "honors", "activities", "references", "achievements", "affiliations"
]
