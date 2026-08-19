"""
ATS business logic.

Ties resume ownership checks, the scorer, and persistence together.
Routers call these functions; they never touch the scorer or the
database directly.
"""
from sqlalchemy.orm import Session

from models.ats_score import AtsScore
from services.ats.scorer import score_resume
from services.resume.service import ResumeNotFoundError, get_resume_for_user


class AtsScoreNotFoundError(Exception):
    """Raised when a requested ATS score doesn't exist or doesn't belong to the user."""


def analyze_resume(db: Session, user_id: int, resume_id: int) -> AtsScore:
    """
    Run ATS analysis on a resume the user owns and persist the result.

    Raises ResumeNotFoundError if the resume doesn't exist or isn't
    owned by this user (propagated from services.resume.service).
    """
    resume = get_resume_for_user(db, user_id=user_id, resume_id=resume_id)

    overall_score, factors = score_resume(
        structured_data=resume.structured_data,
        raw_text=resume.raw_text,
        parsing_status=resume.parsing_status,
    )

    ats_score = AtsScore(
        resume_id=resume.id,
        user_id=user_id,
        overall_score=overall_score,
        factors=[factor.model_dump() for factor in factors],
    )
    db.add(ats_score)
    db.commit()
    db.refresh(ats_score)
    return ats_score


def list_scores_for_resume(db: Session, user_id: int, resume_id: int) -> list[AtsScore]:
    # Ownership check reuses the resume lookup so a user can't enumerate
    # scores for resumes they don't own.
    get_resume_for_user(db, user_id=user_id, resume_id=resume_id)

    return (
        db.query(AtsScore)
        .filter(AtsScore.resume_id == resume_id, AtsScore.user_id == user_id)
        .order_by(AtsScore.created_at.desc())
        .all()
    )


def get_score_for_user(db: Session, user_id: int, score_id: int) -> AtsScore:
    score = (
        db.query(AtsScore)
        .filter(AtsScore.id == score_id, AtsScore.user_id == user_id)
        .first()
    )
    if score is None:
        raise AtsScoreNotFoundError(f"ATS score {score_id} not found")
    return score


__all__ = [
    "analyze_resume",
    "list_scores_for_resume",
    "get_score_for_user",
    "AtsScoreNotFoundError",
    "ResumeNotFoundError",
]