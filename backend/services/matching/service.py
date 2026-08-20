"""
Matching business logic.

Orchestrates keyword, skill, and semantic matching between a resume
and a job, combines them into an overall score, and persists the
result. Routers call these functions; they never touch the
individual matchers or the database directly.
"""
from sqlalchemy.orm import Session

from models.match_result import MatchResult
from services.embeddings.service import get_embedding_provider
from services.job.service import JobNotFoundError, get_job_for_user
from services.matching.keyword_matcher import match_keywords
from services.matching.semantic_matcher import match_semantic
from services.matching.skill_matcher import match_skills
from services.resume.service import ResumeNotFoundError, get_resume_for_user

# Weights for combining sub-scores into the overall match score.
# Skill and keyword matches are concrete/verifiable, so they carry
# more weight than the softer semantic similarity signal.
_WEIGHTS = {"skill": 0.4, "keyword": 0.3, "semantic": 0.3}


class MatchResultNotFoundError(Exception):
    """Raised when a requested match result doesn't exist or doesn't belong to the user."""


def create_match(db: Session, user_id: int, resume_id: int, job_id: int) -> MatchResult:
    """
    Run resume-to-job matching and persist the result.

    Raises ResumeNotFoundError / JobNotFoundError if either doesn't
    exist or isn't owned by this user.
    """
    resume = get_resume_for_user(db, user_id=user_id, resume_id=resume_id)
    job = get_job_for_user(db, user_id=user_id, job_id=job_id)

    resume_text = resume.raw_text or ""
    resume_skills = (resume.structured_data or {}).get("skills") or []

    matched_keywords, missing_keywords, keyword_score = match_keywords(resume_text, job.keywords)
    matched_skills, missing_skills, skill_score = match_skills(resume_skills, job.required_skills)
    semantic_score = match_semantic(resume_text, job.description, get_embedding_provider())

    overall_score = round(
        skill_score * _WEIGHTS["skill"]
        + keyword_score * _WEIGHTS["keyword"]
        + semantic_score * _WEIGHTS["semantic"],
        1,
    )

    match_result = MatchResult(
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        keyword_score=keyword_score,
        semantic_score=semantic_score,
        skill_score=skill_score,
        overall_score=overall_score,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
    )
    db.add(match_result)
    db.commit()
    db.refresh(match_result)
    return match_result


def get_match_for_user(db: Session, user_id: int, match_id: int) -> MatchResult:
    match_result = (
        db.query(MatchResult)
        .filter(MatchResult.id == match_id, MatchResult.user_id == user_id)
        .first()
    )
    if match_result is None:
        raise MatchResultNotFoundError(f"Match result {match_id} not found")
    return match_result


def list_matches_for_resume(db: Session, user_id: int, resume_id: int) -> list[MatchResult]:
    # Ownership check reuses the resume lookup so a user can't enumerate
    # match results for resumes they don't own.
    get_resume_for_user(db, user_id=user_id, resume_id=resume_id)

    return (
        db.query(MatchResult)
        .filter(MatchResult.resume_id == resume_id, MatchResult.user_id == user_id)
        .order_by(MatchResult.created_at.desc())
        .all()
    )


__all__ = [
    "create_match",
    "get_match_for_user",
    "list_matches_for_resume",
    "MatchResultNotFoundError",
    "ResumeNotFoundError",
    "JobNotFoundError",
]