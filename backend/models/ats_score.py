"""
ATS score ORM model.

Stores the outcome of an ATS analysis run: the overall (job-independent)
parsability/quality score and its factor breakdown, plus an optional
job-specific keyword/skill scan - mirroring how real ATS systems work
in practice: a generic parseability check, and a match score against
a specific requisition when one is provided.
"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from services.database.session import Base


class AtsScore(Base):
    __tablename__ = "ats_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)

    # List of factor breakdowns (see schemas/ats.py: AtsFactorResult), stored
    # as-is so the full explanation is preserved exactly as it was computed.
    factors: Mapped[list] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )

    # Optional job-specific keyword/skill scan, present only when the
    # analysis was run with a job_id. See schemas/ats.py: AtsJobMatch.
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    job_match: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )