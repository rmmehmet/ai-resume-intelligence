"""
Skill matching.

Compares the resume's listed skills against the job's required
skills. Pure function, no I/O.
"""


def match_skills(
    resume_skills: list[str], job_required_skills: list[str]
) -> tuple[list[str], list[str], float]:
    """
    Returns (matched_skills, missing_skills, score_0_to_100).
    """
    if not job_required_skills:
        return [], [], 100.0

    resume_skills_lower = {s.lower().strip() for s in resume_skills}
    matched = [skill for skill in job_required_skills if skill.lower() in resume_skills_lower]
    missing = [skill for skill in job_required_skills if skill not in matched]

    score = round((len(matched) / len(job_required_skills)) * 100, 1)
    return matched, missing, score