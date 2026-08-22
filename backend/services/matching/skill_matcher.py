"""
Skill matching.

Compares the resume's listed skills against the job's required
skills. Synonym/acronym-aware: e.g. a resume listing "Kubernetes"
matches a job requiring "K8s" - see services/matching/synonyms.py.
"""
from services.matching.synonyms import expand_terms


def match_skills(
    resume_skills: list[str], job_required_skills: list[str]
) -> tuple[list[str], list[str], float]:
    """
    Returns (matched_skills, missing_skills, score_0_to_100).
    """
    if not job_required_skills:
        return [], [], 100.0

    resume_skills_lower = {s.lower().strip() for s in resume_skills}
    # Expand each of the resume's own skills too, so a resume skill and
    # a job requirement match if either side's synonym set overlaps.
    resume_terms: set[str] = set()
    for skill in resume_skills_lower:
        resume_terms |= expand_terms(skill)

    matched = []
    missing = []
    for skill in job_required_skills:
        if expand_terms(skill) & resume_terms:
            matched.append(skill)
        else:
            missing.append(skill)

    score = round((len(matched) / len(job_required_skills)) * 100, 1)
    return matched, missing, score