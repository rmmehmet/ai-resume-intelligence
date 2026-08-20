"""
Keyword matching.

Checks which of a job's extracted keywords actually appear
somewhere in the resume's raw text. Pure function, no I/O.
"""


def match_keywords(resume_text: str, job_keywords: list[str]) -> tuple[list[str], list[str], float]:
    """
    Returns (matched_keywords, missing_keywords, score_0_to_100).
    """
    if not job_keywords:
        return [], [], 100.0

    lowered_resume = resume_text.lower()
    matched = [kw for kw in job_keywords if kw.lower() in lowered_resume]
    missing = [kw for kw in job_keywords if kw not in matched]

    score = round((len(matched) / len(job_keywords)) * 100, 1)
    return matched, missing, score