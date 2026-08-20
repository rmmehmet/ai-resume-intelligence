"""
Milvus vector store wrapper.

Milvus is used exclusively for vector/semantic search, never as a
source of truth - PostgreSQL owns that role.

At the current scale, a single resume-vs-job comparison is a single
pairwise similarity computation (see services/embeddings), which
doesn't need approximate nearest-neighbor search. Milvus earns its
place once the platform needs to search across many resumes or jobs
at once - e.g. "find the best-matching resumes for this job out of
thousands of candidates."

This wrapper is real, working pymilvus integration - not a stub -
but it is intentionally NOT wired into the current matching flow for
one concrete reason: TfidfEmbeddingProvider fits a fresh vectorizer
per comparison, so its output vectors have a different dimension
every time. Milvus collections require a fixed dimension. Storing
these vectors would not be meaningful.

This becomes usable as soon as a fixed-dimension embedding model
(e.g. sentence-transformers, OpenAI embeddings) is introduced as a
new EmbeddingProvider - a natural pairing with Phase 7's LLM work.
"""
from config import get_settings

settings = get_settings()


class MilvusNotConfiguredError(Exception):
    """Raised when a Milvus operation is attempted without MILVUS_HOST configured."""


class MilvusVectorStore:
    """Thin wrapper around a single Milvus collection of fixed-dimension vectors."""

    def __init__(self, collection_name: str, dimension: int):
        if not settings.milvus_host:
            raise MilvusNotConfiguredError(
                "MILVUS_HOST is not set - Milvus vector search is not available."
            )

        # Imported lazily so the app can run without pymilvus's transitive
        # dependencies being exercised when Milvus isn't configured at all.
        from pymilvus import MilvusClient

        port = settings.milvus_port or "19530"
        uri = f"http://{settings.milvus_host}:{port}"
        self._client = MilvusClient(uri=uri)
        self._collection_name = collection_name

        if not self._client.has_collection(collection_name):
            self._client.create_collection(collection_name=collection_name, dimension=dimension)

    def upsert(self, vector_id: int, vector: list[float], metadata: dict | None = None) -> None:
        record: dict = {"id": vector_id, "vector": vector}
        if metadata:
            record.update(metadata)
        self._client.upsert(collection_name=self._collection_name, data=[record])

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        results = self._client.search(
            collection_name=self._collection_name, data=[vector], limit=top_k
        )
        return results[0] if results else []