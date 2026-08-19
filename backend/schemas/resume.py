"""
Pydantic schemas for resume upload and retrieval.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.resume import ParsingStatus


class ContactInfo(BaseModel):
    """Best-effort extracted contact details."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None


class StructuredResume(BaseModel):
    """
    A best-effort structured breakdown of a resume's raw text.

    Section detection is heuristic (keyword/section-header based) in
    Phase 3. Nothing here is AI-generated yet - that comes in Phase 7.
    """

    contact: ContactInfo = ContactInfo()
    summary: str | None = None
    experience: list[str] = []
    education: list[str] = []
    skills: list[str] = []
    projects: list[str] = []


class ResumeRead(BaseModel):
    """Public-facing representation of a resume."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_type: str
    file_size_bytes: int
    parsing_status: ParsingStatus
    parsing_error: str | None
    structured_data: dict | None
    created_at: datetime


class ResumeSummary(BaseModel):
    """Lightweight representation used in list views (no raw text/structured data)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_type: str
    parsing_status: ParsingStatus
    created_at: datetime