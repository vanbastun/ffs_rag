"""Test script to verify reranker works correctly"""

import pytest
from src.rag_core.rerankers import CrossEncoderReranker

def test_reranker():
    """Test that reranker can load and work."""
    print("Testing CrossEncoder reranker...")
    
    try:
        # Initialize reranker
        reranker = CrossEncoderReranker(
            model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
            lazy=True  # Don't load immediately
        )
        print("✓ Reranker initialized successfully")
        
        # Test reranking
        query = "What does it cost?"
        candidates = [
            ("We offer monthly and annual subscriptions.", {"id": "1"}),
            ("You can find pricing information on our website.", {"id": "2"}),
            ("Our service is completely free to use.", {"id": "3"}),
        ]
        
        print(f"Reranking {len(candidates)} candidates for query: '{query}'")
        reranked = reranker.rerank(query, candidates, return_scores=True)
        
        print("✓ Reranking completed successfully")
        print("Results:")
        for i, (text, meta, score) in enumerate(reranked):
            print(f"  {i+1}. Score: {score:.3f} - {text[:50]}...")
            
    except Exception as e:
        print(f"✗ Reranker test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_reranker()
