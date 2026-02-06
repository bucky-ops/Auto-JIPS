from __future__ import annotations

import re

from ajips.app.api.schemas import AnalyzeRequest, AnalyzeResponse
from ajips.app.services.critique import critique_requirements, analyze_job_quality
from ajips.app.services.enrichment import infer_hidden_skills
from ajips.app.services.extraction import extract_skills, extract_experience_level, extract_education_requirements
from ajips.app.services.ingestion import fetch_job_posting
from ajips.app.services.normalization import normalize_text
from ajips.app.services.profiling import build_focus_areas, identify_role_type
from ajips.app.services.resume_match import compute_resume_alignment


def extract_job_title(text: str) -> str:
    """
    Attempt to extract job title from the posting text.
    """
    # Common patterns for job titles
    patterns = [
        r'(?:position|role|title):\s*([^\n]+)',
        r'(?:hiring|seeking|looking for)\s+(?:a\s+)?([^\n,]+?)(?:\s+to|\s+who|\s+with)',
        r'^([A-Z][^\n]{10,60}?)(?:\s*[-–—]\s*|\n)',  # Title at start
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            title = match.group(1).strip()
            # Clean up common artifacts
            title = re.sub(r'\s+', ' ', title)
            if 5 < len(title) < 100:
                return title
    
    return None


def build_job_profile(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Build a comprehensive job profile from the input payload.
    Orchestrates all analysis services to produce detailed insights.
    """
    # Step 1: Get raw text from URL or direct input
    raw_text = payload.job_posting.text
    if not raw_text and payload.job_posting.url:
        try:
            raw_text = fetch_job_posting(payload.job_posting.url)
        except Exception as e:
            raw_text = f"Error fetching URL: {str(e)}"
    
    if not raw_text:
        raw_text = ""
    
    # Step 2: Normalize text
    normalized = normalize_text(raw_text)
    
    # Step 3: Extract job title
    title = extract_job_title(raw_text)
    
    # Step 4: Extract explicit skills
    explicit_skills = extract_skills(normalized)
    
    # Step 5: Infer hidden skills
    hidden_skills = infer_hidden_skills(explicit_skills)
    
    # Step 6: Critique requirements
    critiques = critique_requirements(normalized)
    
    # Step 7: Build focus areas
    focus_areas = build_focus_areas(explicit_skills)
    
    # Step 8: Identify role type
    identified_role = identify_role_type(explicit_skills)
    
    # Step 9: Extract additional metadata
    experience_level = extract_experience_level(normalized)
    education_reqs = extract_education_requirements(normalized)
    
    # Step 10: Analyze job quality
    quality_analysis = analyze_job_quality(normalized)
    
    # Step 11: Resume alignment (if provided)
    resume_alignment = None
    if payload.resume_text:
        resume_alignment = compute_resume_alignment(payload.resume_text, explicit_skills)
    
    # Step 12: Generate summary
    summary = generate_summary(
        title=title or identified_role,
        explicit_skills=explicit_skills,
        hidden_skills=hidden_skills,
        focus_areas=focus_areas,
        experience_level=experience_level,
        quality_analysis=quality_analysis
    )
    
    return AnalyzeResponse(
        title=title or identified_role,
        focus_areas=focus_areas,
        explicit_skills=explicit_skills,
        hidden_skills=hidden_skills,
        critiques=critiques,
        resume_alignment=resume_alignment,
        summary=summary,
    )


def generate_summary(
    title: str,
    explicit_skills: list,
    hidden_skills: list,
    focus_areas: list,
    experience_level: str,
    quality_analysis: dict
) -> str:
    """
    Generate a human-readable summary of the job profile.
    """
    parts = []
    
    # Title and role
    parts.append(f"**{title}** ({experience_level})")
    
    # Skills summary
    if explicit_skills:
        top_skills = explicit_skills[:5]
        parts.append(f"Key skills: {', '.join(top_skills)}")
    
    # Focus areas
    if focus_areas:
        top_focus = focus_areas[0]
        parts.append(f"Primary focus: {top_focus.name} ({int(top_focus.weight * 100)}% match)")
    
    # Hidden skills insight
    if hidden_skills:
        parts.append(f"Inferred {len(hidden_skills)} hidden skills that may be valuable")
    
    # Quality assessment
    grade = quality_analysis.get('grade', 'N/A')
    parts.append(f"Job posting quality: {grade}")
    
    return " | ".join(parts)
