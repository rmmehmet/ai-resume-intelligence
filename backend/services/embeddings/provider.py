"""
Embedding / semantic similarity provider abstraction.

External providers must be abstracted behind an interface so they
can be swapped without touching business logic.

`embed()` is the primitive: every concrete provider must turn text
into a fixed-dimension vector. `similarity()` has a default
implementation (cosine similarity of the two embeddings) so most
providers only need to implement `embed()`. A provider whose
vectors are NOT fixed-dimension (e.g. a per-comparison TF-IDF fit)
should override `similarity()` directly and raise from `embed()`
instead of pretending to support it.
"""
import math
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Return a fixed-dimension vector embedding for `text`."""
        raise NotImplementedError

    def similarity(self, text_a: str, text_b: str) -> float:
        """Return a 0.0-1.0 semantic similarity score between two texts."""
        if not text_a.strip() or not text_b.strip():
            return 0.0
        return cosine_similarity(self.embed(text_a), self.embed(text_b))


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Cosine similarity between two equal-length vectors, clamped to [0, 1]."""
    if not vec_a or not vec_b:
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0

    score = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, score))