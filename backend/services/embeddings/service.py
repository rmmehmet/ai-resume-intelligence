"""
Embedding provider factory.

Single place that decides which EmbeddingProvider implementation is
active. Swapping to a real embedding model later means changing
this function, not any of its callers.
"""
from services.embeddings.provider import EmbeddingProvider
from services.embeddings.tfidf_provider import TfidfEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    return TfidfEmbeddingProvider()