"""
TF-IDF based similarity provider.

A lightweight, dependency-free (no external API, no model download)
fallback for environments where sentence-transformers isn't
available or a model download isn't possible. Computes cosine
similarity between two documents' TF-IDF vectors.

This provider overrides `similarity()` directly rather than
implementing `embed()`, because its vectors are fit per-comparison
and therefore have a different dimension every call - unsuitable
for a fixed-dimension embedding column or a Milvus index. Use
SentenceBertEmbeddingProvider (services/embeddings/sentence_bert_provider.py)
when fixed-dimension embeddings are needed.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity

from services.embeddings.provider import EmbeddingProvider


class TfidfEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError(
            "TfidfEmbeddingProvider vectors are not fixed-dimension "
            "(fit per-comparison) - use similarity() instead of embed()."
        )

    def similarity(self, text_a: str, text_b: str) -> float:
        if not text_a.strip() or not text_b.strip():
            return 0.0

        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform([text_a, text_b])
        except ValueError:
            # Empty vocabulary after stopword removal (e.g. both texts
            # were trivially short) - no meaningful similarity to compute.
            return 0.0

        score = sk_cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(max(0.0, min(1.0, score)))