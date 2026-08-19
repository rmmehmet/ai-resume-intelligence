"""
Resume router.

Routers only receive requests, validate input, call a service, and
return a response - no business logic lives here.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_db
from models.user import User
from schemas.resume import ResumeRead, ResumeSummary
from services.resume import service as resume_service
from services.resume.storage import FileTooLargeError, UnsupportedFileTypeError

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeRead:
    content = await file.read()

    try:
        resume = resume_service.upload_and_parse_resume(
            db, user_id=current_user.id, filename=file.filename or "", content=content
        )
    except (UnsupportedFileTypeError, FileTooLargeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return resume


@router.get("", response_model=list[ResumeSummary])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeSummary]:
    return resume_service.list_resumes_for_user(db, user_id=current_user.id)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeRead:
    try:
        return resume_service.get_resume_for_user(db, user_id=current_user.id, resume_id=resume_id)
    except resume_service.ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc