"""
ATS business logic.

Ties resume ownership checks, the scorer, and persistence together.
Routers call these functions; they never touch the scorer or the
database directly.
"""
from sqlalchemy.orm import Session

from models.ats_score import AtsScore
from schemas.ats import AtsJobMatch
from services.ats.scorer import score_resume
from services.job.service import JobNotFoundError, get_job_for_user
from services.matching.keyword_matcher import match_keywords
from services.matching.skill_matcher import match_skills
from services.resume.service import ResumeNotFoundError, get_resume_for_user


class AtsScoreNotFoundError(Exception):
    """Raised when a requested ATS score doesn't exist or doesn't belong to the user."""


def _run_job_match(db: Session, user_id: int, resume, job_id: int) -> AtsJobMatch:
    """
    Job-specific keyword/skill scan - the part of ATS analysis that
    mirrors how a real ATS screens a resume against a specific
    requisition, rather than judging the resume in the abstract.
    """
    job = get_job_for_user(db, user_id=user_id, job_id=job_id)

    resume_text = resume.raw_text or ""
    resume_skills = (resume.structured_data or {}).get("skills") or []

    matched_keywords, missing_keywords, keyword_score = match_keywords(resume_text, job.keywords)
    matched_skills, missing_skills, skill_score = match_skills(resume_skills, job.required_skills)

    # Skills matter more than incidental keyword overlap for a
    # requisition-specific screen - weighted accordingly.
    match_score = round(skill_score * 0.6 + keyword_score * 0.4, 1)

    return AtsJobMatch(
        job_id=job.id,
        job_title=job.title,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
    )


def analyze_resume(
    db: Session, user_id: int, resume_id: int, job_id: int | None = None
) -> AtsScore:
    """
    Run ATS analysis on a resume the user owns and persist the result.

    If `job_id` is given, also runs a job-specific keyword/skill scan
    against that job (must also be owned by the user).

    Raises ResumeNotFoundError / JobNotFoundError if either doesn't
    exist or isn't owned by this user.
    """
    resume = get_resume_for_user(db, user_id=user_id, resume_id=resume_id)

    overall_score, factors = score_resume(
        structured_data=resume.structured_data,
        raw_text=resume.raw_text,
        parsing_status=resume.parsing_status,
        layout_analysis=resume.layout_analysis,
    )

    job_match = _run_job_match(db, user_id, resume, job_id) if job_id is not None else None

    ats_score = AtsScore(
        resume_id=resume.id,
        user_id=user_id,
        overall_score=overall_score,
        factors=[factor.model_dump() for factor in factors],
        job_id=job_id,
        job_match=job_match.model_dump() if job_match else None,
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
    "JobNotFoundError",
]