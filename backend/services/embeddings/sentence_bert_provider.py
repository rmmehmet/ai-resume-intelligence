"""
Sentence-BERT embedding provider.

The primary EmbeddingProvider implementation: real semantic
embeddings via sentence-transformers, producing fixed-dimension
vectors (384 for the default model). This is what powers genuine
semantic matching (not just word-overlap) and what makes storing
vectors in a fixed-dimension index like Milvus meaningful.

The model is downloaded automatically from Hugging Face the first
time it's used (~90MB for the default model) and cached locally
under the standard Hugging Face cache directory afterwards - no
manual download step needed, but the machine running this needs
outbound internet access on first use.
"""
from sentence_transformers import SentenceTransformer

from config import get_settings
from services.embeddings.provider import EmbeddingProvider

settings = get_settings()

# all-MiniLM-L6-v2: 384 dimensions, fast on CPU, strong general-purpose
# quality/speed tradeoff - a standard default for this kind of task.
# Swappable via EMBEDDING_MODEL_NAME if a larger/more accurate model is
# preferred later (dimension must be updated to match if changed).
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

_model_cache: dict[str, SentenceTransformer] = {}


def _get_model(model_name: str) -> SentenceTransformer:
    """Load and cache the model so it's only initialized once per process."""
    if model_name not in _model_cache:
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]


class SentenceBertEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model_name or DEFAULT_MODEL_NAME
        self._model = _get_model(self.model_name)

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            return [0.0] * EMBEDDING_DIMENSION
        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()