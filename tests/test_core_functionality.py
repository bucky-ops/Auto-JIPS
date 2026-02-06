"""
Basic tests for AJIPS core functionality
"""
import pytest
from ajips.app.services.extraction import extract_skills, extract_experience_level, extract_education_requirements
from ajips.app.services.enrichment import infer_hidden_skills
from ajips.app.services.critique import critique_requirements
from ajips.app.services.profiling import build_focus_areas, identify_role_type


def test_skill_extraction():
    """Test basic skill extraction"""
    text = "We need a backend engineer with Python, PostgreSQL, AWS, and Docker experience."
    skills = extract_skills(text)
    
    assert "python" in skills
    assert "postgresql" in skills
    assert "aws" in skills
    assert "docker" in skills


def test_multi_word_skill_extraction():
    """Test multi-word skill extraction"""
    text = "Looking for someone with machine learning and natural language processing experience."
    skills = extract_skills(text)
    
    assert "machine learning" in skills
    assert "natural language processing" in skills


def test_experience_level_extraction():
    """Test experience level detection"""
    text1 = "Entry-level position for recent graduates"
    text2 = "Senior engineer with 7+ years of experience"
    text3 = "Mid-level developer needed"
    
    assert extract_experience_level(text1) == "Entry Level"
    assert extract_experience_level(text2) == "Senior Level"
    assert extract_experience_level(text3) == "Mid Level"


def test_education_requirements():
    """Test education requirement extraction"""
    text = "Bachelor's degree required. Master's degree preferred. Relevant certifications a plus."
    reqs = extract_education_requirements(text)
    
    assert "Bachelor's Degree" in reqs
    assert "Master's Degree" in reqs
    assert "Professional Certification" in reqs


def test_hidden_skill_inference():
    """Test hidden skill inference"""
    explicit_skills = ["python", "kubernetes", "aws"]
    hidden_skills = infer_hidden_skills(explicit_skills)
    
    # Should infer related skills
    assert len(hidden_skills) > 0
    # Python-related skills
    assert any(skill in hidden_skills for skill in ["testing", "pip", "pytest"])
    # Kubernetes-related skills
    assert any(skill in hidden_skills for skill in ["helm", "kubectl"])
    # AWS-related skills
    assert any(skill in hidden_skills for skill in ["iam", "vpc", "s3"])


def test_critique_entry_level_contradiction():
    """Test critique for entry-level contradictions"""
    text = "Entry-level position requiring 5 years of experience"
    critiques = critique_requirements(text)
    
    # Should flag the contradiction
    assert any(c.severity == "warning" for c in critiques)
    assert any("entry" in c.message.lower() for c in critiques)


def test_critique_missing_salary():
    """Test critique for missing salary information"""
    text = "Backend engineer needed with Python skills"
    critiques = critique_requirements(text)
    
    # Should note missing salary
    assert any("salary" in c.message.lower() for c in critiques)


def test_critique_vague_cloud():
    """Test critique for vague cloud requirements"""
    text = "Must have cloud experience"
    critiques = critique_requirements(text)
    
    # Should flag vague cloud requirement
    assert any("cloud" in c.message.lower() and "unspecified" in c.message.lower() for c in critiques)


def test_focus_area_building():
    """Test focus area categorization"""
    skills = ["python", "fastapi", "postgresql", "aws", "docker", "react"]
    focus_areas = build_focus_areas(skills)
    
    # Should have multiple focus areas
    assert len(focus_areas) > 0
    
    # Should include backend
    backend_areas = [fa for fa in focus_areas if "backend" in fa.name.lower()]
    assert len(backend_areas) > 0
    
    # Should include cloud
    cloud_areas = [fa for fa in focus_areas if "cloud" in fa.name.lower()]
    assert len(cloud_areas) > 0


def test_role_identification():
    """Test role type identification"""
    backend_skills = ["python", "fastapi", "postgresql", "api"]
    frontend_skills = ["react", "javascript", "html", "css"]
    data_skills = ["python", "pandas", "machine learning", "scikit-learn"]
    
    assert "backend" in identify_role_type(backend_skills).lower()
    assert "frontend" in identify_role_type(frontend_skills).lower()
    assert "data" in identify_role_type(data_skills).lower()


def test_empty_input_handling():
    """Test handling of empty inputs"""
    assert extract_skills("") == []
    assert extract_experience_level("") == "Not Specified"
    assert len(critique_requirements("")) > 0  # Should still provide feedback
    assert len(build_focus_areas([])) > 0  # Should return general category


def test_comprehensive_job_posting():
    """Test with a realistic job posting"""
    job_text = """
    Senior Backend Engineer
    
    We are seeking an experienced backend engineer with 5+ years of experience.
    
    Requirements:
    - Strong Python and FastAPI experience
    - PostgreSQL database design and optimization
    - AWS cloud infrastructure (EC2, S3, Lambda)
    - Docker and Kubernetes for containerization
    - RESTful API design
    - Agile development methodology
    
    Nice to have:
    - Machine learning experience
    - React for frontend work
    
    We offer competitive salary, remote work, and great benefits.
    """
    
    skills = extract_skills(job_text)
    hidden_skills = infer_hidden_skills(skills)
    critiques = critique_requirements(job_text)
    focus_areas = build_focus_areas(skills)
    experience = extract_experience_level(job_text)
    
    # Verify comprehensive analysis
    assert len(skills) >= 5
    assert len(hidden_skills) > 0
    assert len(critiques) > 0
    assert len(focus_areas) >= 2
    assert experience == "Senior Level"
    
    # Verify specific skills detected
    assert "python" in skills
    assert "fastapi" in skills
    assert "postgresql" in skills
    assert "aws" in skills
    assert "docker" in skills
    assert "kubernetes" in skills
    
    # Should not flag major issues since it's well-written
    critical_critiques = [c for c in critiques if c.severity == "critical"]
    assert len(critical_critiques) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
