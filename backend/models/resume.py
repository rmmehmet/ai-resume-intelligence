"""
Resume ORM model.

Stores the uploaded file's metadata, the raw extracted text, and a
best-effort structured breakdown of that text. Business logic for
parsing/structuring lives in services/resume, not here.
"""
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from services.database.session import Base


class ParsingStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "pdf" | "docx"
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Fixed-dimension semantic embedding of raw_text (see
    # services/embeddings/sentence_bert_provider.py), computed once at
    # parse time and reused for every job match instead of recomputing
    # it on every comparison.
    embedding: Mapped[list | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    # JSONB on PostgreSQL, plain JSON on SQLite (dev) - same column, different
    # storage under the hood, handled automatically by SQLAlchemy's dialect.
    structured_data: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    # Structural ATS-parsability signals (multi-column, tables, contact
    # info location, etc.) - see services/resume/layout_analyzer.py.
    layout_analysis: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=True
    )

    parsing_status: Mapped[ParsingStatus] = mapped_column(
        Enum(ParsingStatus), default=ParsingStatus.PENDING, nullable=False
    )
    parsing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )