"""
Resume business logic.

Orchestrates storage, text extraction, and structuring. Routers call
these functions; they never touch storage/extraction/structuring or
the database directly.
"""
from sqlalchemy.orm import Session

from models.resume import ParsingStatus, Resume
from services.embeddings.service import get_embedding_provider
from services.embeddings.vector_store import try_upsert
from services.resume import storage
from services.resume.extractor import TextExtractionError, extract_text
from services.resume.layout_analyzer import analyze_layout
from services.resume.structurer import structure_resume_text

RESUME_VECTOR_COLLECTION = "resume_embeddings"


class ResumeNotFoundError(Exception):
    """Raised when a requested resume doesn't exist or doesn't belong to the user."""


def upload_and_parse_resume(
    db: Session,
    user_id: int,
    filename: str,
    content: bytes,
) -> Resume:
    """
    Validate, store, extract text from, and structure an uploaded resume.

    Parsing failures are captured on the Resume record rather than
    raised, so the upload itself still succeeds and the user can see
    what went wrong.
    """
    extension = storage.validate_upload(filename, len(content))
    storage_path = storage.save_file(content, extension, user_id)

    resume = Resume(
        user_id=user_id,
        original_filename=filename,
        file_type=extension,
        storage_path=storage_path,
        file_size_bytes=len(content),
        parsing_status=ParsingStatus.PENDING,
    )

    try:
        raw_text = extract_text(content, extension)
        structured = structure_resume_text(raw_text)

        resume.raw_text = raw_text
        resume.structured_data = structured.model_dump()
        resume.parsing_status = ParsingStatus.SUCCEEDED

        # Structural ATS-parsability signals (multi-column, tables,
        # header/footer-only contact info) - computed once here since it
        # requires the original file bytes, which aren't kept around.
        resume.layout_analysis = analyze_layout(content, extension).model_dump()

        # Compute the embedding once here so every future job match reuses
        # it instead of re-running the model on every comparison. Not every
        # provider can produce a storable embedding (e.g. TfidfEmbeddingProvider
        # fits per-comparison) - if so, leave it unset; matching falls back
        # to computing similarity from raw text on the fly.
        provider = get_embedding_provider()
        try:
            resume.embedding = provider.embed(raw_text)
        except NotImplementedError:
            resume.embedding = None
    except TextExtractionError as exc:
        resume.parsing_status = ParsingStatus.FAILED
        resume.parsing_error = str(exc)

    db.add(resume)
    db.commit()
    db.refresh(resume)

    if resume.embedding:
        try_upsert(RESUME_VECTOR_COLLECTION, len(resume.embedding), resume.id, resume.embedding)

    return resume


def list_resumes_for_user(db: Session, user_id: int) -> list[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )


def get_resume_for_user(db: Session, user_id: int, resume_id: int) -> Resume:
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == user_id)
        .first()
    )
    if resume is None:
        raise ResumeNotFoundError(f"Resume {resume_id} not found")
    return resume