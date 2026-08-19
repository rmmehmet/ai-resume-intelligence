"""
Heuristic structuring of resume text into sections.

This is intentionally rule-based (keyword/section-header detection),
not AI-powered - LLM-assisted understanding comes in Phase 7. The
goal here is a reasonable best-effort structure, not perfection.
"""
import re

from schemas.resume import ContactInfo, StructuredResume

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")

# Section header keywords, ordered by the section they map to. Matching is
# case-insensitive and expects the line to be short (a heading, not a
# sentence that happens to contain the word).
_SECTION_KEYWORDS: dict[str, list[str]] = {
    "summary": ["summary", "profile", "objective", "about me"],
    "experience": ["experience", "work history", "employment"],
    "education": ["education", "academic background"],
    "skills": ["skills", "technical skills", "competencies"],
    "projects": ["projects", "personal projects"],
}

_MAX_HEADING_LENGTH = 40


def _detect_section(line: str) -> str | None:
    """Return the section name if `line` looks like a section heading, else None."""
    stripped = line.strip()
    if not stripped or len(stripped) > _MAX_HEADING_LENGTH:
        return None

    lowered = stripped.lower().strip(":")
    for section, keywords in _SECTION_KEYWORDS.items():
        if lowered in keywords:
            return section
    return None


def _extract_contact(text: str) -> ContactInfo:
    email_match = _EMAIL_PATTERN.search(text)
    phone_match = _PHONE_PATTERN.search(text)

    # Heuristic: the resume's name is often the first non-empty line,
    # as long as it doesn't look like contact info itself.
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), None)
    name = None
    if first_line and not _EMAIL_PATTERN.search(first_line) and len(first_line) <= _MAX_HEADING_LENGTH:
        name = first_line

    return ContactInfo(
        name=name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0).strip() if phone_match else None,
    )


def structure_resume_text(raw_text: str) -> StructuredResume:
    """Turn raw resume text into a best-effort StructuredResume."""
    lines = raw_text.splitlines()

    sections: dict[str, list[str]] = {name: [] for name in _SECTION_KEYWORDS}
    current_section: str | None = None

    for line in lines:
        detected = _detect_section(line)
        if detected is not None:
            current_section = detected
            continue

        if current_section is not None and line.strip():
            sections[current_section].append(line.strip())

    contact = _extract_contact(raw_text)
    summary_text = " ".join(sections["summary"]) if sections["summary"] else None

    return StructuredResume(
        contact=contact,
        summary=summary_text,
        experience=sections["experience"],
        education=sections["education"],
        skills=_split_skills(sections["skills"]),
        projects=sections["projects"],
    )


def _split_skills(skill_lines: list[str]) -> list[str]:
    """Skills sections are often comma/bullet separated on one or few lines."""
    skills: list[str] = []
    for line in skill_lines:
        parts = re.split(r"[,•|]", line)
        skills.extend(part.strip() for part in parts if part.strip())
    return skills