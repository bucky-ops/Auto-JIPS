from typing import List, Optional

from pydantic import BaseModel, Field


class JobPostingInput(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None


class AnalyzeRequest(BaseModel):
    job_posting: JobPostingInput
    resume_text: Optional[str] = None


class FocusArea(BaseModel):
    name: str
    weight: float
    skills: List[str]


class CritiqueItem(BaseModel):
    severity: str = Field(..., pattern="^(info|warning|critical)$")
    message: str


class AnalyzeResponse(BaseModel):
    title: Optional[str] = Field(None, description="Extracted job title")
    focus_areas: List[FocusArea] = Field(
        default_factory=list, description="Primary focus areas"
    )
    explicit_skills: List[str] = Field(
        default_factory=list, description="Explicitly mentioned skills"
    )
    hidden_skills: List[str] = Field(
        default_factory=list, description="Inferred skills"
    )
    critiques: List[CritiqueItem] = Field(
        default_factory=list, description="Job posting critiques"
    )
    salary_range: Optional[dict] = Field(None, description="Extracted salary range")
    interview_stages: List[str] = Field(
        default_factory=list, description="Detected interview stages"
    )
    quality_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Job posting quality score (0–100)"
    )
    resume_alignment: Optional[float] = Field(
        None, description="Resume alignment score (0–1)"
    )
    summary: str
