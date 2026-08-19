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


class AtsScoreRead(BaseModel):
    """Public-facing representation of a completed ATS analysis."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    overall_score: float
    factors: list[AtsFactorResult]
    created_at: datetime