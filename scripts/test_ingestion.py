#!/usr/bin/env python3
"""Test script to verify ingestion works correctly"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rag_core.config import Settings
from src.rag_core.bm25_qdrant import BM25QdrantClient
from src.rag_core.vectorstore_qdrant import QdrantVectorStore

def test_collections():
    """Test that both collections exist and have data."""
    s = Settings()
    
    # Test dense vector collection
    print("Testing dense vector collection...")
    vs = QdrantVectorStore(s.qdrant_url)
    try:
        collection_info = vs.client.get_collection("documents")
        print(f"✓ Dense collection exists: {collection_info.vectors_count} vectors")
    except Exception as e:
        print(f"✗ Dense collection error: {e}")
    
    # Test BM25 collection
    print("Testing BM25 collection...")
    bm25 = BM25QdrantClient(s.qdrant_url)
    try:
        collection_info = bm25.client.get_collection("bm25_documents")
        print(f"✓ BM25 collection exists: {collection_info.vectors_count} vectors")
    except Exception as e:
        print(f"✗ BM25 collection error: {e}")
    
    # Test search
    print("Testing BM25 search...")
    try:
        results = bm25.search("What does it cost?", k=3)
        print(f"✓ BM25 search works: {len(results)} results")
        for i, (doc_id, meta, score) in enumerate(results):
            print(f"  {i+1}. Score: {score:.3f}, Question: {meta.get('question', 'N/A')[:50]}...")
    except Exception as e:
        print(f"✗ BM25 search error: {e}")

if __name__ == "__main__":
    test_collections()
