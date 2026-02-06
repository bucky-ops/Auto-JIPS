from __future__ import annotations

from typing import List

from ajips.app.api.schemas import FocusArea
from ajips.app.services.extraction import SKILL_DATABASE, categorize_skills


# Enhanced focus area mappings aligned with skill database
FOCUS_AREA_MAP = {
    "Backend Development": {"python", "java", "go", "rust", "c#", "django", "flask", "fastapi", 
                           "spring", "express", "node.js", "api", "rest", "graphql"},
    "Frontend Development": {"javascript", "typescript", "react", "angular", "vue", "html", "css",
                            "next.js", "svelte", "redux", "webpack"},
    "Cloud & Infrastructure": {"aws", "azure", "gcp", "docker", "kubernetes", "terraform", 
                              "ansible", "cloudformation", "serverless"},
    "Data Engineering": {"spark", "airflow", "kafka", "hadoop", "flink", "databricks", "snowflake"},
    "Data Science & ML": {"machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
                         "pandas", "numpy", "data science", "ai"},
    "Database Management": {"postgresql", "mysql", "mongodb", "redis", "cassandra", "elasticsearch",
                           "sql", "database"},
    "DevOps & CI/CD": {"jenkins", "github actions", "gitlab ci", "circleci", "docker", "kubernetes",
                      "ci/cd", "devops", "monitoring"},
    "Mobile Development": {"ios", "android", "react native", "flutter", "swift", "kotlin"},
    "Security": {"oauth", "jwt", "saml", "sso", "encryption", "security", "penetration testing"},
    "Project Management": {"agile", "scrum", "kanban", "jira", "project management", "leadership"}
}


def build_focus_areas(explicit_skills: List[str]) -> List[FocusArea]:
    """
    Build focus areas from explicit skills with improved categorization and weighting.
    """
    if not explicit_skills:
        return [FocusArea(name="General", weight=1.0, skills=[])]
    
    focus_areas: List[FocusArea] = []
    skill_lower_set = {skill.lower() for skill in explicit_skills}
    
    # Calculate matches for each focus area
    for area, keywords in FOCUS_AREA_MAP.items():
        matched = [skill for skill in explicit_skills if skill.lower() in keywords]
        if matched:
            # Weight based on both count and percentage
            count_weight = len(matched) / max(len(explicit_skills), 1)
            coverage_weight = len(matched) / max(len(keywords), 1)
            # Combined weight favoring both breadth and depth
            weight = round((count_weight * 0.7 + coverage_weight * 0.3), 2)
            focus_areas.append(FocusArea(name=area, weight=weight, skills=matched))
    
    # If no focus areas matched, create a general category
    if not focus_areas:
        focus_areas.append(FocusArea(name="General Technology", weight=1.0, skills=explicit_skills))
    else:
        # Sort by weight descending
        focus_areas.sort(key=lambda x: x.weight, reverse=True)
    
    return focus_areas


def identify_role_type(explicit_skills: List[str]) -> str:
    """
    Identify the most likely role type based on skills.
    """
    skill_text = " ".join(explicit_skills).lower()
    
    role_patterns = {
        "Data Scientist": ["python", "machine learning", "statistics", "pandas", "scikit-learn"],
        "Backend Engineer": ["python", "java", "api", "database", "sql"],
        "Frontend Developer": ["react", "javascript", "html", "css", "typescript"],
        "Full Stack Developer": ["react", "node.js", "javascript", "database"],
        "DevOps Engineer": ["docker", "kubernetes", "aws", "terraform", "ci/cd"],
        "Data Engineer": ["spark", "airflow", "kafka", "python", "sql"],
        "Machine Learning Engineer": ["tensorflow", "pytorch", "machine learning", "python"],
        "Cloud Architect": ["aws", "azure", "gcp", "terraform", "cloud"],
        "Mobile Developer": ["ios", "android", "react native", "flutter", "swift", "kotlin"]
    }
    
    best_match = "Software Engineer"
    max_matches = 0
    
    for role, keywords in role_patterns.items():
        matches = sum(1 for keyword in keywords if keyword in skill_text)
        if matches > max_matches:
            max_matches = matches
            best_match = role
    
    return best_match if max_matches >= 2 else "Software Engineer"


def calculate_skill_diversity(explicit_skills: List[str]) -> dict:
    """
    Calculate diversity metrics for the skill set.
    Returns metrics about skill distribution across categories.
    """
    if not explicit_skills:
        return {"diversity_score": 0, "categories": {}, "is_specialized": False}
    
    # Categorize skills
    categorized = categorize_skills(explicit_skills)
    
    # Calculate diversity score (0-1, higher = more diverse)
    num_categories = len(categorized)
    diversity_score = min(num_categories / 5, 1.0)  # Normalize to max of 5 categories
    
    # Determine if specialized (>60% skills in one category)
    is_specialized = False
    if categorized:
        max_category_size = max(len(skills) for skills in categorized.values())
        if max_category_size / len(explicit_skills) > 0.6:
            is_specialized = True
    
    return {
        "diversity_score": round(diversity_score, 2),
        "categories": {cat: len(skills) for cat, skills in categorized.items()},
        "is_specialized": is_specialized,
        "primary_category": max(categorized.items(), key=lambda x: len(x[1]))[0] if categorized else "general"
    }
