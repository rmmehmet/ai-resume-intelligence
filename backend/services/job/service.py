"""
Job business logic.

Orchestrates requirement parsing, embedding, and persistence.
Routers call these functions; they never touch the parser or the
database directly.
"""
from sqlalchemy.orm import Session

from models.job import Job
from schemas.job import JobCreate
from services.embeddings.service import get_embedding_provider
from services.embeddings.vector_store import try_upsert
from services.job.parser import parse_job_requirements

JOB_VECTOR_COLLECTION = "job_embeddings"


class JobNotFoundError(Exception):
    """Raised when a requested job doesn't exist or doesn't belong to the user."""


def create_job(db: Session, user_id: int, job_in: JobCreate) -> Job:
    """Parse a job description's requirements, embed it, and persist it."""
    required_skills, keywords = parse_job_requirements(job_in.description)

    provider = get_embedding_provider()
    try:
        embedding = provider.embed(job_in.description)
    except NotImplementedError:
        embedding = None

    job = Job(
        user_id=user_id,
        title=job_in.title,
        description=job_in.description,
        required_skills=required_skills,
        keywords=keywords,
        embedding=embedding,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if embedding:
        try_upsert(JOB_VECTOR_COLLECTION, len(embedding), job.id, embedding)

    return job


def list_jobs_for_user(db: Session, user_id: int) -> list[Job]:
    return (
        db.query(Job)
        .filter(Job.user_id == user_id)
        .order_by(Job.created_at.desc())
        .all()
    )


def get_job_for_user(db: Session, user_id: int, job_id: int) -> Job:
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    if job is None:
        raise JobNotFoundError(f"Job {job_id} not found")
    return job