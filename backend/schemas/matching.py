"""
Pydantic schemas for resume-to-job match results.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchResultRead(BaseModel):
    """Public-facing representation of a resume-to-job match."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    job_id: int

    keyword_score: float
    semantic_score: float
    skill_score: float
    overall_score: float

    matched_keywords: list[str]
    missing_keywords: list[str]
    matched_skills: list[str]
    missing_skills: list[str]

    created_at: datetime