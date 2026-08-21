"""
Milvus vector store wrapper.

Milvus is used exclusively for vector/semantic search, never as a
source of truth - PostgreSQL owns that role. Resume and job
embeddings are computed once (at upload/creation time) and stored
both on the row itself (for fast direct comparisons - see
services/matching/semantic_matcher.py) and, if Milvus is configured,
upserted here too.

Direct comparison (cosine similarity between two stored vectors) is
all a single resume-vs-job match needs and doesn't require Milvus at
all. Milvus earns its place once the platform needs to search across
many resumes or jobs at once - e.g. "find the best-matching resumes
for this job out of thousands of candidates." That kind of endpoint
isn't built yet, but every embedding is already being upserted here
so it's a small addition later, not a re-architecture.

Configuration (see .env.example):
- MILVUS_URI: preferred. Works for both a managed Zilliz Cloud
  endpoint and a self-hosted Milvus URI (e.g. "http://localhost:19530").
- MILVUS_TOKEN: API token, only needed for Zilliz Cloud.
- MILVUS_HOST / MILVUS_PORT: convenience fallback for a plain
  self-hosted instance if MILVUS_URI isn't set.

None of these are required - if nothing is configured, upsert() and
search() raise MilvusNotConfiguredError, and callers treat that as
optional/best-effort (see services/matching/service.py).
"""
from config import get_settings

settings = get_settings()


class MilvusNotConfiguredError(Exception):
    """Raised when a Milvus operation is attempted without Milvus configured."""


def _resolve_uri() -> str | None:
    if settings.milvus_uri:
        return settings.milvus_uri
    if settings.milvus_host:
        port = settings.milvus_port or "19530"
        return f"http://{settings.milvus_host}:{port}"
    return None


class MilvusVectorStore:
    """Thin wrapper around a single Milvus collection of fixed-dimension vectors."""

    def __init__(self, collection_name: str, dimension: int):
        uri = _resolve_uri()
        if not uri:
            raise MilvusNotConfiguredError(
                "Milvus is not configured (set MILVUS_URI, or MILVUS_HOST/MILVUS_PORT) "
                "- vector search is unavailable."
            )

        # Imported lazily so the app can run without pymilvus's transitive
        # dependencies being exercised when Milvus isn't configured at all.
        from pymilvus import MilvusClient

        self._client = MilvusClient(uri=uri, token=settings.milvus_token or None)
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


def try_upsert(collection_name: str, dimension: int, vector_id: int, vector: list[float]) -> None:
    """
    Best-effort upsert: silently does nothing if Milvus isn't configured.

    Used from business logic (e.g. after computing a resume/job
    embedding) where Milvus is an optional enhancement, not a
    requirement for the request to succeed.
    """
    try:
        store = MilvusVectorStore(collection_name, dimension)
        store.upsert(vector_id, vector)
    except MilvusNotConfiguredError:
        pass