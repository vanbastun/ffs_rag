import uuid
from typing import List, Tuple, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import SparseVectorParams, Modifier, Document, PointStruct


class BM25QdrantClient:
    """BM25 client using Qdrant's sparse vector capabilities."""
    
    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "bm25_documents"):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create BM25 collection if it does not exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Create collection with BM25 sparse vector configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                sparse_vectors_config={
                    "bm25": SparseVectorParams(
                        modifier=Modifier.IDF,
                    )
                }
            )
    
    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """Insert documents into BM25 collection.
        
        Args:
            documents: List of dicts with 'text', 'id', and other metadata
        """
        points = []
        for doc in documents:
            point_id = doc.get("id", uuid.uuid4().hex)
            
            points.append(PointStruct(
                id=point_id,
                vector={
                    "bm25": Document(
                        text=doc["text"], 
                        model="Qdrant/bm25",
                    ),
                },
                payload={
                    "text": doc["text"],
                    "id": doc["id"],
                    **{k: v for k, v in doc.items() if k not in ["text", "id"]}
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
    
    def search(self, query: str, k: int = 10) -> List[Tuple[str, Dict[str, Any], float]]:
        """Search using BM25.
        
        Args:
            query: Search query text
            k: Number of results to return
            
        Returns:
            List of (doc_id, metadata, score) tuples
        """
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=Document(
                text=query,
                model="Qdrant/bm25",
            ),
            using="bm25",
            limit=k,
            with_payload=True,
        )
        
        hits = []
        for result in results.points:
            doc_id = result.id
            metadata = dict(result.payload)
            score = float(result.score)
            hits.append((doc_id, metadata, score))
        
        return hits
