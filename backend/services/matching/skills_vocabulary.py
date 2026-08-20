"""
Shared skills vocabulary.

A moderate, non-exhaustive list of common technical/professional
skills used to detect required skills inside free-text job
descriptions (which rarely have a clean "Skills:" section the way
resumes do). Matching is case-insensitive, whole-word.

This is intentionally simple and swappable - a more complete
taxonomy or an LLM-based extractor (Phase 7+) can replace it later
without changing how callers use `find_skills_in_text`.
"""
import re

KNOWN_SKILLS: set[str] = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "r", "scala", "kotlin", "swift", "php", "ruby",
    # Web / frameworks
    "react", "vue", "angular", "node.js", "next.js", "fastapi", "django",
    "flask", "spring", "spring boot", "express",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "keras",
    "machine learning", "deep learning", "nlp", "computer vision",
    "data analysis", "data science", "etl",
    # Infra / DevOps
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "jenkins", "linux", "git", "github actions", "nginx",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "milvus",
    "sqlite", "oracle",
    # General / soft skills
    "leadership", "communication", "project management", "agile", "scrum",
    "problem solving", "teamwork", "mentoring",
}


def find_skills_in_text(text: str) -> list[str]:
    """Return the subset of KNOWN_SKILLS that appear in `text` (whole-word, case-insensitive)."""
    lowered = text.lower()
    found = []
    for skill in KNOWN_SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, lowered):
            found.append(skill)
    return sorted(found)