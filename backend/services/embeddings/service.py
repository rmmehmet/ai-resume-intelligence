"""
Embedding provider factory.

Single place that decides which EmbeddingProvider implementation is
active, controlled by EMBEDDING_PROVIDER in settings. Callers never
instantiate a provider directly - swapping providers means changing
this function (or the env var), not any calling code.
"""
from functools import lru_cache

from config import get_settings
from services.embeddings.provider import EmbeddingProvider

settings = get_settings()


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    provider_name = settings.embedding_provider.lower()

    if provider_name == "sentence-bert":
        from services.embeddings.sentence_bert_provider import SentenceBertEmbeddingProvider
        return SentenceBertEmbeddingProvider()

    if provider_name == "tfidf":
        from services.embeddings.tfidf_provider import TfidfEmbeddingProvider
        return TfidfEmbeddingProvider()

    raise ValueError(
        f"Unknown EMBEDDING_PROVIDER '{settings.embedding_provider}'. "
        "Expected 'sentence-bert' or 'tfidf'."
    )