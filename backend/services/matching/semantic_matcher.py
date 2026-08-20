"""
Semantic matching.

Scores overall textual similarity between a resume and a job
description using the configured EmbeddingProvider.
"""
from services.embeddings.provider import EmbeddingProvider


def match_semantic(resume_text: str, job_description: str, provider: EmbeddingProvider) -> float:
    """Returns a 0-100 semantic similarity score."""
    similarity = provider.similarity(resume_text, job_description)
    return round(similarity * 100, 1)