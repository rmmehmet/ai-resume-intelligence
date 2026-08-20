"""
Job router.

Routers only receive requests, validate input, call a service, and
return a response - no business logic lives here.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_db
from models.user import User
from schemas.job import JobCreate, JobRead, JobSummary
from services.job import service as job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobRead:
    return job_service.create_job(db, user_id=current_user.id, job_in=job_in)


@router.get("", response_model=list[JobSummary])
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[JobSummary]:
    return job_service.list_jobs_for_user(db, user_id=current_user.id)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobRead:
    try:
        return job_service.get_job_for_user(db, user_id=current_user.id, job_id=job_id)
    except job_service.JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc