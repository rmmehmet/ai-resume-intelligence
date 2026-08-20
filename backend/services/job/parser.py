"""
Job description parsing.

Extracts required skills (via the shared skills vocabulary) and
general keywords (via simple word-frequency analysis) from a pasted
job description. Heuristic, not AI-powered - same philosophy as
services/resume/structurer.py.
"""
import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from services.matching.skills_vocabulary import find_skills_in_text

_WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z+#.-]{2,}")
_MAX_KEYWORDS = 25


def extract_keywords(text: str, exclude: set[str] | None = None) -> list[str]:
    """
    Extract the most frequent significant words from `text`.

    Excludes English stopwords and anything in `exclude` (typically
    the already-detected skills, so keywords don't just repeat them).
    """
    exclude = {word.lower() for word in (exclude or set())}
    raw_words = [w.lower() for w in _WORD_PATTERN.findall(text)]
    # Strip trailing punctuation (e.g. a sentence-ending "." caught by the
    # pattern's allowance for "." inside terms like "c#"/"node.js").
    words = [w.strip(".,;:!?") for w in raw_words]

    significant = [
        w for w in words
        if w and w not in ENGLISH_STOP_WORDS and w not in exclude and len(w) >= 3
    ]

    counts = Counter(significant)
    most_common = [word for word, _ in counts.most_common(_MAX_KEYWORDS)]
    return sorted(most_common)


def parse_job_requirements(description: str) -> tuple[list[str], list[str]]:
    """
    Parse a job description into (required_skills, keywords).

    required_skills come from vocabulary matching; keywords are the
    remaining frequent significant terms not already captured as a skill.
    """
    required_skills = find_skills_in_text(description)
    keywords = extract_keywords(description, exclude=set(required_skills))
    return required_skills, keywords