"""
Individual ATS scoring rules.

Each rule is a pure function: given the resume's structured data,
raw text, and parsing status, it returns one AtsFactorResult. Rules
know nothing about the database, HTTP, or each other - the scorer
(scorer.py) is what runs them all and aggregates the result.

Point values across all rules sum to 100, so overall_score is
directly interpretable as a percentage.
"""
import re

from models.resume import ParsingStatus
from schemas.ats import AtsFactorResult

_ACTION_VERBS = {
    "built", "led", "designed", "managed", "developed", "implemented",
    "created", "launched", "improved", "reduced", "increased", "optimized",
    "architected", "delivered", "automated", "deployed", "analyzed",
    "coordinated", "mentored", "founded", "migrated", "streamlined",
}

_DIGIT_PATTERN = re.compile(r"\d")


def rule_parsability(*, parsing_status: ParsingStatus, **_) -> AtsFactorResult:
    """A resume that failed to parse can't be read by an ATS either."""
    points_possible = 10.0
    passed = parsing_status == ParsingStatus.SUCCEEDED
    return AtsFactorResult(
        key="parsability",
        label="File parses cleanly",
        points_earned=points_possible if passed else 0.0,
        points_possible=points_possible,
        passed=passed,
        explanation=(
            "The file's text was extracted successfully."
            if passed
            else "The file could not be parsed - ATS systems will likely fail to read it too."
        ),
    )


def rule_contact_completeness(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 10.0
    contact = structured.get("contact") or {}
    present = [bool(contact.get(field)) for field in ("name", "email", "phone")]
    earned = points_possible * (sum(present) / len(present))
    return AtsFactorResult(
        key="contact_completeness",
        label="Contact information complete",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=all(present),
        explanation=(
            f"Found {sum(present)}/3 contact fields (name, email, phone). "
            "ATS systems and recruiters both rely on this being easy to find."
        ),
    )


def rule_has_summary(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 5.0
    summary = (structured.get("summary") or "").strip()
    passed = len(summary) >= 20
    return AtsFactorResult(
        key="has_summary",
        label="Has a professional summary",
        points_earned=points_possible if passed else 0.0,
        points_possible=points_possible,
        passed=passed,
        explanation=(
            "A summary section was found."
            if passed
            else "No meaningful summary/objective section was detected."
        ),
    )


def rule_section_coverage(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 20.0
    sections = ["experience", "education", "skills", "projects"]
    present = [bool(structured.get(s)) for s in sections]
    per_section = points_possible / len(sections)
    earned = per_section * sum(present)
    missing = [s for s, ok in zip(sections, present) if not ok]
    return AtsFactorResult(
        key="section_coverage",
        label="Standard resume sections present",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=not missing,
        explanation=(
            "All standard sections (experience, education, skills, projects) were found."
            if not missing
            else f"Missing or undetected sections: {', '.join(missing)}."
        ),
    )


def rule_quantifiable_achievements(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 15.0
    experience_lines: list[str] = structured.get("experience") or []
    if not experience_lines:
        return AtsFactorResult(
            key="quantifiable_achievements",
            label="Achievements include numbers/metrics",
            points_earned=0.0,
            points_possible=points_possible,
            passed=False,
            explanation="No experience bullet points were found to evaluate.",
        )

    with_numbers = [line for line in experience_lines if _DIGIT_PATTERN.search(line)]
    ratio = len(with_numbers) / len(experience_lines)
    earned = points_possible * ratio
    return AtsFactorResult(
        key="quantifiable_achievements",
        label="Achievements include numbers/metrics",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=ratio >= 0.5,
        explanation=(
            f"{len(with_numbers)}/{len(experience_lines)} experience lines include a number "
            "(e.g. '40% faster', 'led a team of 5'). Quantified impact scores better with ATS "
            "and recruiters alike."
        ),
    )


def rule_action_verb_usage(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 15.0
    experience_lines: list[str] = structured.get("experience") or []
    if not experience_lines:
        return AtsFactorResult(
            key="action_verb_usage",
            label="Bullet points start with strong action verbs",
            points_earned=0.0,
            points_possible=points_possible,
            passed=False,
            explanation="No experience bullet points were found to evaluate.",
        )

    def starts_with_action_verb(line: str) -> bool:
        first_word = line.strip().split(" ")[0].lower().strip(".,:;")
        return first_word in _ACTION_VERBS

    matching = [line for line in experience_lines if starts_with_action_verb(line)]
    ratio = len(matching) / len(experience_lines)
    earned = points_possible * ratio
    return AtsFactorResult(
        key="action_verb_usage",
        label="Bullet points start with strong action verbs",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=ratio >= 0.5,
        explanation=(
            f"{len(matching)}/{len(experience_lines)} experience lines start with an action verb "
            "(e.g. 'Built', 'Led', 'Designed')."
        ),
    )


def rule_skills_count(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 10.0
    skills: list[str] = structured.get("skills") or []
    target = 5
    earned = min(points_possible, points_possible * (len(skills) / target))
    return AtsFactorResult(
        key="skills_count",
        label="Sufficient listed skills",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=len(skills) >= target,
        explanation=f"{len(skills)} skills listed (target: {target}+).",
    )


def rule_resume_length(*, raw_text: str, **_) -> AtsFactorResult:
    points_possible = 15.0
    word_count = len(raw_text.split())
    ideal_min, ideal_max = 300, 800

    if ideal_min <= word_count <= ideal_max:
        earned = points_possible
        passed = True
        explanation = f"{word_count} words - within the ideal range ({ideal_min}-{ideal_max})."
    elif word_count < ideal_min:
        earned = points_possible * (word_count / ideal_min)
        passed = False
        explanation = f"{word_count} words - shorter than the ideal minimum of {ideal_min}."
    else:
        # Penalize overly long resumes, but not as harshly as too-short ones.
        overflow_ratio = min(1.0, (word_count - ideal_max) / ideal_max)
        earned = points_possible * (1 - overflow_ratio * 0.5)
        passed = False
        explanation = f"{word_count} words - longer than the ideal maximum of {ideal_max}."

    return AtsFactorResult(
        key="resume_length",
        label="Resume length is appropriate",
        points_earned=round(max(0.0, earned), 1),
        points_possible=points_possible,
        passed=passed,
        explanation=explanation,
    )


# Order here determines the order factors appear in the response.
ALL_RULES = [
    rule_parsability,
    rule_contact_completeness,
    rule_has_summary,
    rule_section_coverage,
    rule_quantifiable_achievements,
    rule_action_verb_usage,
    rule_skills_count,
    rule_resume_length,
]