"""
Individual ATS scoring rules.

Each rule is a pure function: given the resume's structured data,
raw text, parsing status, and layout analysis, it returns one
AtsFactorResult. Rules know nothing about the database, HTTP, or
each other - the scorer (scorer.py) is what runs them all and
aggregates the result.

Point values across all rules sum to 100, so overall_score is
directly interpretable as a percentage. Weighted toward genuine ATS
*parsing* risk (layout, tables, header/footer placement, garbled
text) rather than pure resume-writing style, since those are the
failure modes that cause a real ATS to misread or drop content
entirely - not just look less polished.
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


def rule_section_coverage(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 15.0
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
            else f"Missing or undetected sections: {', '.join(missing)}. "
            "Non-standard section headers can cause an ATS to miss their content entirely."
        ),
    )


def rule_layout_compatibility(*, layout: dict, **_) -> AtsFactorResult:
    """
    Real ATS parsers extract text in reading order and are well known
    to scramble multi-column layouts and mangle table content. This is
    one of the most common reasons a qualified candidate's resume gets
    misread - not a style preference.
    """
    points_possible = 15.0
    issues = []
    if layout.get("multi_column"):
        issues.append("multi-column layout")
    if layout.get("has_tables"):
        issues.append("table structure")

    if not issues:
        return AtsFactorResult(
            key="layout_compatibility",
            label="Layout is ATS-parseable (no columns/tables)",
            points_earned=points_possible,
            points_possible=points_possible,
            passed=True,
            explanation="No multi-column layout or table structures detected.",
        )

    # Multi-column is generally the more severe risk (affects the whole
    # document's reading order); a table is often more contained.
    penalty = points_possible if "multi-column layout" in issues else points_possible * 0.5
    earned = max(0.0, points_possible - penalty)
    return AtsFactorResult(
        key="layout_compatibility",
        label="Layout is ATS-parseable (no columns/tables)",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=False,
        explanation=(
            f"Detected: {', '.join(issues)}. Many ATS parsers read text left-to-right across "
            "the whole page, which scrambles multi-column content, and often drop or reorder "
            "table cell contents."
        ),
    )


def rule_header_footer_contact(*, layout: dict, **_) -> AtsFactorResult:
    """Many ATS parsers strip document headers/footers before parsing the body."""
    points_possible = 10.0
    at_risk = bool(layout.get("contact_only_in_header_footer"))
    return AtsFactorResult(
        key="header_footer_contact",
        label="Contact info is in the document body",
        points_earned=0.0 if at_risk else points_possible,
        points_possible=points_possible,
        passed=not at_risk,
        explanation=(
            "Contact info appears only in a document header/footer - many ATS parsers strip "
            "these before reading the resume, which can make a candidate unreachable."
            if at_risk
            else "Contact info is present in the main body of the document."
        ),
    )


def rule_text_extraction_integrity(*, layout: dict, raw_text: str, **_) -> AtsFactorResult:
    """A resume that's mostly an embedded image yields little to no extractable text."""
    points_possible = 10.0
    garbled_ratio = float(layout.get("garbled_text_ratio", 0.0))
    has_enough_text = len(raw_text.strip()) >= 50

    if garbled_ratio <= 0.02 and has_enough_text:
        return AtsFactorResult(
            key="text_extraction_integrity",
            label="Text extracts cleanly",
            points_earned=points_possible,
            points_possible=points_possible,
            passed=True,
            explanation="Extracted text looks clean, with no signs of image-based or corrupted content.",
        )

    earned = points_possible * max(0.0, 1 - garbled_ratio * 10)
    if not has_enough_text:
        earned = min(earned, points_possible * 0.2)

    return AtsFactorResult(
        key="text_extraction_integrity",
        label="Text extracts cleanly",
        points_earned=round(earned, 1),
        points_possible=points_possible,
        passed=False,
        explanation=(
            "Very little text could be extracted - the resume may be image-based, which most "
            "ATS parsers cannot read at all."
            if not has_enough_text
            else "Extracted text contains unusual/corrupted characters, suggesting an encoding "
            "or embedded-image issue."
        ),
    )


def rule_quantifiable_achievements(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 5.0
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
            "(e.g. '40% faster', 'led a team of 5')."
        ),
    )


def rule_action_verb_usage(*, structured: dict, **_) -> AtsFactorResult:
    points_possible = 5.0
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
    points_possible = 10.0
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
# Points: 10 + 10 + 15 + 15 + 10 + 10 + 5 + 5 + 10 + 10 = 100
ALL_RULES = [
    rule_parsability,
    rule_contact_completeness,
    rule_section_coverage,
    rule_layout_compatibility,
    rule_header_footer_contact,
    rule_text_extraction_integrity,
    rule_quantifiable_achievements,
    rule_action_verb_usage,
    rule_skills_count,
    rule_resume_length,
]