"""
TF-IDF based similarity provider.

The current concrete implementation of EmbeddingProvider. Computes
cosine similarity between two documents' TF-IDF vectors - a
lightweight, dependency-free (no external API, no model download)
stand-in for true semantic embeddings.

Note: TF-IDF vectors here are fit per-comparison, so their dimension
varies between calls - they are NOT suitable for storing in a
persistent vector index like Milvus. A fixed-dimension embedding
model would be needed for that (see services/embeddings/vector_store.py).
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.embeddings.provider import EmbeddingProvider


class TfidfEmbeddingProvider(EmbeddingProvider):
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

        score = cosine_similarity(matrix[0], matrix[1])[0][0]
        return float(max(0.0, min(1.0, score)))