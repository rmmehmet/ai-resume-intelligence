"""
Semantic matching.

Scores overall textual similarity between a resume and a job
description. Prefers using pre-computed embeddings (fast: just a
cosine similarity, no model inference) and falls back to computing
similarity from raw text on the fly if either embedding is missing -
e.g. a resume/job created before embeddings were introduced, or a
provider (like TF-IDF) that doesn't produce storable embeddings.
"""
from services.embeddings.provider import EmbeddingProvider, cosine_similarity


def match_semantic(
    *,
    provider: EmbeddingProvider,
    resume_text: str,
    job_description: str,
    resume_embedding: list[float] | None,
    job_embedding: list[float] | None,
) -> float:
    """Returns a 0-100 semantic similarity score."""
    if resume_embedding and job_embedding:
        similarity = cosine_similarity(resume_embedding, job_embedding)
    else:
        similarity = provider.similarity(resume_text, job_description)

    return round(similarity * 100, 1)