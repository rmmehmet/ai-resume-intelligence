"""
Job description parsing.

Extracts required skills (via the shared skills vocabulary) and
general keywords from a pasted job description. Heuristic, not
AI-powered - same philosophy as services/resume/structurer.py.

Keyword extraction covers both single words and two-word phrases
("machine learning", "project management"), since compound terms
often carry more signal than either word alone in a job posting.
It also filters out job-posting boilerplate ("responsibilities",
"looking", "candidate", ...) in addition to standard English
stopwords - plain frequency + stopword filtering alone tends to
surface generic filler rather than genuinely distinctive terms.
"""
import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from services.matching.skills_vocabulary import find_skills_in_text

_WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z+#.-]{2,}")
_MAX_KEYWORDS = 25

# Words that are common filler in job postings specifically, not caught by
# general English stopword lists (which target function words, not
# domain-generic nouns/verbs like "responsibilities" or "looking").
_JOB_BOILERPLATE_STOPWORDS = {
    "experience", "experienced", "role", "roles", "team", "teams", "work",
    "working", "looking", "candidate", "candidates", "responsibilities",
    "requirements", "required", "requires", "opportunity", "opportunities",
    "company", "join", "environment", "ability", "strong", "excellent",
    "years", "year", "including", "etc", "using", "used", "use", "new",
    "across", "within", "related", "preferred", "plus", "skills", "skill",
    "knowledge", "understanding", "familiarity", "position", "job", "day",
    "days", "based", "help", "level", "responsible",
}


def _normalize_words(text: str) -> list[str]:
    raw_words = [w.lower() for w in _WORD_PATTERN.findall(text)]
    # Strip trailing punctuation (e.g. a sentence-ending "." caught by the
    # pattern's allowance for "." inside terms like "c#"/"node.js").
    return [w.strip(".,;:!?") for w in raw_words if w]


def _is_significant(word: str, exclude: set[str]) -> bool:
    return (
        len(word) >= 3
        and word not in ENGLISH_STOP_WORDS
        and word not in _JOB_BOILERPLATE_STOPWORDS
        and word not in exclude
    )


def extract_keywords(text: str, exclude: set[str] | None = None) -> list[str]:
    """
    Extract the most frequent significant unigrams and bigrams from `text`.

    Excludes English + job-boilerplate stopwords and anything in
    `exclude` (typically the already-detected skills, so keywords
    don't just repeat them). Unigrams that are already covered by a
    selected bigram (e.g. "machine" when "machine learning" is
    present) are dropped to avoid redundant entries.
    """
    exclude = {word.lower() for word in (exclude or set())}
    words = _normalize_words(text)

    unigram_counts = Counter(w for w in words if _is_significant(w, exclude))

    bigrams = [f"{a} {b}" for a, b in zip(words, words[1:])]
    bigram_counts = Counter(
        bg for bg in bigrams
        if all(_is_significant(w, exclude) for w in bg.split(" "))
    )
    # A bigram appearing only once is usually noise, not a real phrase.
    bigram_counts = Counter({bg: c for bg, c in bigram_counts.items() if c >= 2})

    selected_bigrams = [bg for bg, _ in bigram_counts.most_common(_MAX_KEYWORDS // 2)]
    covered_words = {w for bg in selected_bigrams for w in bg.split(" ")}

    remaining_slots = _MAX_KEYWORDS - len(selected_bigrams)
    selected_unigrams = [
        w for w, _ in unigram_counts.most_common(_MAX_KEYWORDS)
        if w not in covered_words
    ][:remaining_slots]

    return sorted(selected_bigrams + selected_unigrams)


def parse_job_requirements(description: str) -> tuple[list[str], list[str]]:
    """
    Parse a job description into (required_skills, keywords).

    required_skills come from vocabulary matching; keywords are the
    remaining frequent significant terms not already captured as a
    skill. Individual words of multi-word skills (e.g. "computer" and
    "vision" from "computer vision") are also excluded from keywords,
    so they don't leak back in as redundant unigrams.
    """
    required_skills = find_skills_in_text(description)

    exclude = set(required_skills)
    for skill in required_skills:
        exclude.update(skill.split(" "))

    keywords = extract_keywords(description, exclude=exclude)
    return required_skills, keywords