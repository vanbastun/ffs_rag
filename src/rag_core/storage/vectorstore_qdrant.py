import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class QdrantVectorStore:
    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "documents"):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection if it does not exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection with 512-dimensional vectors (jinaai/jina-embeddings-v2-small-en)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE),
            )

    def upsert_document(self, meta: dict) -> str:
        """Create or update document, return document_id."""
        document_id = meta.get("source_id", str(uuid.uuid4()))

        # Store document metadata (currently unused but kept for future use)
        # doc_meta = {
        #     "source_id": meta["source_id"],
        #     "title": meta.get("title", ""),
        #     "uri": meta.get("uri", ""),
        #     "lang": meta.get("lang", ""),
        #     "version": meta.get("version", 1),
        #     "hash": meta.get("hash", ""),
        #     "created_at": meta.get("created_at", ""),
        # }

        # Use source_id as unique document identifier
        return document_id

    def insert_chunks(
        self, doc_id: str, texts: list[str], metas: list[dict[str, Any]], vecs: Any
    ) -> None:
        """Insert chunks with embeddings into Qdrant."""
        points = []
        for i, (text, meta, vec) in enumerate(zip(texts, metas, vecs, strict=False)):
            point_id = i  # Use integer ID
            point_meta = {
                "document_id": doc_id,
                "chunk_ix": i,
                "text": text,
                "source_id": meta.get("source_id", doc_id),
                "lang": meta.get("lang", ""),
                **meta,
            }

            points.append(PointStruct(id=point_id, vector=vec.tolist(), payload=point_meta))

        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self, qvec: Any, k: int = 5, filters: dict | None = None
    ) -> list[tuple[str, dict[str, Any], float]]:
        """Search for similar vectors."""
        query_filter = None
        if filters and "lang" in filters:
            query_filter = Filter(
                must=[FieldCondition(key="lang", match=MatchValue(value=filters["lang"]))]
            )

        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=qvec.tolist(),
            limit=k,
            query_filter=query_filter,
            with_payload=True,
        )

        hits = []
        for result in search_results:
            meta = dict(result.payload)
            meta["document_id"] = meta.get("document_id", "")
            meta["chunk_ix"] = meta.get("chunk_ix", 0)
            meta["source_id"] = (
                f"{meta.get('source_id', meta.get('document_id'))}#{meta.get('chunk_ix', 0)}"
            )

            hits.append((meta.get("text", ""), meta, float(result.score)))

        return hits
