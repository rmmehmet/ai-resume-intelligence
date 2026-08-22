"""
Pydantic schemas for ATS analysis results.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AtsFactorResult(BaseModel):
    """
    A single scored factor within the ATS analysis.

    Kept explicit and self-contained so the score is explainable: a
    user (or the frontend) can see exactly why points were earned or
    lost for each factor.
    """

    key: str
    label: str
    points_earned: float
    points_possible: float
    passed: bool
    explanation: str


class AtsJobMatch(BaseModel):
    """
    Optional job-specific keyword/skill scan, present when ATS analysis
    is run against a particular job posting - this is the part that
    most closely mirrors how a real ATS screens a resume for a specific
    requisition (literal keyword/skill presence, synonym-aware).
    """

    job_id: int
    job_title: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]


class AtsScoreRead(BaseModel):
    """Public-facing representation of a completed ATS analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    overall_score: float
    factors: list[AtsFactorResult]
    job_match: AtsJobMatch | None = None
    created_at: datetime