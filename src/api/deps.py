from functools import lru_cache

from src.rag_core.config import Settings
from src.rag_core.embeddings import FastEmbedEmbeddings
from src.rag_core.generation import Generator, OpenRouterLLM
from src.rag_core.pipeline import SimpleRAG
from src.rag_core.retrieval import CrossEncoderReranker, HybridRetriever
from src.rag_core.storage import BM25QdrantClient, QdrantVectorStore


@lru_cache
def get_settings() -> Settings:
    """Get application settings with caching.

    Returns:
        Settings instance loaded from environment variables
    """
    return Settings()


def get_rag() -> SimpleRAG:
    """Get configured RAG pipeline instance.

    Returns:
        SimpleRAG instance with configured components

    Note:
        Uses OpenRouter LLM if API key is provided, otherwise DummyLLM
        Pre-warms models to avoid download delays on first API call
    """
    s = get_settings()

    # Pre-warm embedding model
    print("Pre-warming embedding model...")
    emb = FastEmbedEmbeddings(s.embedding_model)

    # Pre-warm reranker model
    print("Pre-warming reranker model...")
    rr = CrossEncoderReranker(s.reranker_model, lazy=False)  # Force immediate loading

    # Initialize other components (these may fail if services aren't running)
    try:
        vs = QdrantVectorStore(s.qdrant_url)
        bm25 = BM25QdrantClient(s.qdrant_url)
        retr = HybridRetriever(bm25=bm25, vs=vs, reranker=rr, alpha=0.5)
    except Exception as e:
        print(f"Warning: Could not connect to Qdrant ({e})")
        print("Models are pre-warmed, but storage services need to be running")
        # Return a minimal RAG instance for testing
        retr = None

    # Use OpenRouter if API key is provided, otherwise use DummyLLM
    if s.openrouter_api_key:
        llm = OpenRouterLLM(s.openrouter_model)
        generator = Generator(emb, llm)
        return SimpleRAG(emb, retr, generator)
    else:
        return SimpleRAG(emb, retr)
