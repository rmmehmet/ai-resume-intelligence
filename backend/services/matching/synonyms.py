"""
Synonym / acronym groups for keyword and skill matching.

Real recruiters and good ATS systems don't penalize a candidate for
writing "SEO" when the job posting says "Search Engine Optimization"
- they're the same thing. A naive substring matcher misses this
constantly, which is one of the most common complaints about
low-quality ATS keyword matching. This module lets matchers treat
known equivalent terms as the same keyword.

Each group is a set of interchangeable lowercase terms. This is a
practical, non-exhaustive list - not a full ontology - and can grow
over time without touching any matching logic.
"""
SYNONYM_GROUPS: list[set[str]] = [
    {"seo", "search engine optimization"},
    {"ml", "machine learning"},
    {"ai", "artificial intelligence"},
    {"nlp", "natural language processing"},
    {"cv", "computer vision"},
    {"ci/cd", "continuous integration", "continuous deployment", "continuous delivery"},
    {"ui", "user interface"},
    {"ux", "user experience"},
    {"ui/ux", "user interface", "user experience"},
    {"qa", "quality assurance"},
    {"pm", "project manager", "project management"},
    {"k8s", "kubernetes"},
    {"js", "javascript"},
    {"ts", "typescript"},
    {"api", "application programming interface"},
    {"db", "database"},
    {"oop", "object oriented programming"},
    {"crm", "customer relationship management"},
    {"erp", "enterprise resource planning"},
    {"b2b", "business to business"},
    {"b2c", "business to consumer"},
    {"roi", "return on investment"},
    {"kpi", "key performance indicator"},
    {"saas", "software as a service"},
    {"aws", "amazon web services"},
    {"gcp", "google cloud platform"},
    {"cs", "computer science"},
    {"hr", "human resources"},
    {"vp", "vice president"},
    {"devops", "development operations"},
    {"sre", "site reliability engineering"},
    {"llm", "large language model"},
]

_TERM_TO_GROUP: dict[str, set[str]] = {}
for _group in SYNONYM_GROUPS:
    for _term in _group:
        _TERM_TO_GROUP[_term] = _group


def expand_terms(term: str) -> set[str]:
    """Return `term` plus any known synonyms/acronym expansions for it."""
    normalized = term.lower().strip()
    return _TERM_TO_GROUP.get(normalized, {normalized})