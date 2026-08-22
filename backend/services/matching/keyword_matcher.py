"""
Keyword matching.

Checks which of a job's extracted keywords actually appear
somewhere in the resume's raw text. Synonym/acronym-aware: a
keyword counts as matched if it, or any known equivalent term
(e.g. "SEO" / "search engine optimization"), appears in the text -
plain substring matching alone misses this constantly and is one of
the most common complaints about low-quality ATS matching.
"""
from services.matching.synonyms import expand_terms


def match_keywords(resume_text: str, job_keywords: list[str]) -> tuple[list[str], list[str], float]:
    """
    Returns (matched_keywords, missing_keywords, score_0_to_100).
    """
    if not job_keywords:
        return [], [], 100.0

    lowered_resume = resume_text.lower()

    matched = []
    missing = []
    for keyword in job_keywords:
        candidates = expand_terms(keyword)
        if any(candidate in lowered_resume for candidate in candidates):
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = round((len(matched) / len(job_keywords)) * 100, 1)
    return matched, missing, score