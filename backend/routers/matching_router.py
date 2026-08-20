"""
Matching router.

Routers only receive requests, validate input, call a service, and
return a response - no business logic lives here.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_db
from models.user import User
from schemas.matching import MatchResultRead
from services.job.service import JobNotFoundError
from services.matching import service as matching_service
from services.resume.service import ResumeNotFoundError

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post(
    "/resumes/{resume_id}/jobs/{job_id}",
    response_model=MatchResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_match(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchResultRead:
    try:
        return matching_service.create_match(
            db, user_id=current_user.id, resume_id=resume_id, job_id=job_id
        )
    except (ResumeNotFoundError, JobNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/resumes/{resume_id}/results", response_model=list[MatchResultRead])
def list_matches(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MatchResultRead]:
    try:
        return matching_service.list_matches_for_resume(
            db, user_id=current_user.id, resume_id=resume_id
        )
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/results/{match_id}", response_model=MatchResultRead)
def get_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchResultRead:
    try:
        return matching_service.get_match_for_user(db, user_id=current_user.id, match_id=match_id)
    except matching_service.MatchResultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc