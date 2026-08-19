"""
ATS score ORM model.

Stores the outcome of an ATS analysis run: the overall score and the
full factor-by-factor breakdown that explains it. Business logic for
computing the score lives in services/ats, not here.
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )