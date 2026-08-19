"""
ATS scorer.

Runs every rule in services/ats/rules.py against a resume and
aggregates the results into an overall score. This module has no
database access - it operates purely on data passed into it.
"""
from models.resume import ParsingStatus
from schemas.ats import AtsFactorResult
from services.ats.rules import ALL_RULES


def score_resume(
    *,
    structured_data: dict | None,
    raw_text: str | None,
    parsing_status: ParsingStatus,
) -> tuple[float, list[AtsFactorResult]]:
    """
    Compute an explainable ATS score for a resume.

    Returns (overall_score_0_to_100, factor_breakdown).
    """
    structured = structured_data or {}
    text = raw_text or ""

    factors = [
        rule(structured=structured, raw_text=text, parsing_status=parsing_status)
        for rule in ALL_RULES
    ]

    total_possible = sum(f.points_possible for f in factors)
    total_earned = sum(f.points_earned for f in factors)
    overall_score = round((total_earned / total_possible) * 100, 1) if total_possible else 0.0

    return overall_score, factors