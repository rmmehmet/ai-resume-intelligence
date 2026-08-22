"""
ATS router.

Routers only receive requests, validate input, call a service, and
return a response - no business logic lives here.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_db
from models.user import User
from schemas.ats import AtsScoreRead
from services.ats import service as ats_service
from services.resume.service import ResumeNotFoundError

router = APIRouter(prefix="/api/ats", tags=["ats"])


@router.post(
    "/resumes/{resume_id}/analyze",
    response_model=AtsScoreRead,
    status_code=status.HTTP_201_CREATED,
)
def analyze_resume(
    resume_id: int,
    job_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtsScoreRead:
    """
    Run ATS analysis on a resume.

    Pass `job_id` as a query param (?job_id=5) to also run a
    job-specific keyword/skill scan against that job posting.
    """
    try:
        return ats_service.analyze_resume(
            db, user_id=current_user.id, resume_id=resume_id, job_id=job_id
        )
    except (ResumeNotFoundError, ats_service.JobNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/resumes/{resume_id}/scores", response_model=list[AtsScoreRead])
def list_scores(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AtsScoreRead]:
    try:
        return ats_service.list_scores_for_resume(db, user_id=current_user.id, resume_id=resume_id)
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/scores/{score_id}", response_model=AtsScoreRead)
def get_score(
    score_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AtsScoreRead:
    try:
        return ats_service.get_score_for_user(db, user_id=current_user.id, score_id=score_id)
    except ats_service.AtsScoreNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc