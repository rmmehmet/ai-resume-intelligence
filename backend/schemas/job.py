"""
Pydantic schemas for job descriptions.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    """Payload for submitting a job description for analysis."""

    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=20)


class JobRead(BaseModel):
    """Public-facing representation of an analyzed job."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    required_skills: list[str]
    keywords: list[str]
    created_at: datetime


class JobSummary(BaseModel):
    """Lightweight representation used in list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime