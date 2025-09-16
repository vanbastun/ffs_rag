from functools import lru_cache

from src.rag_core.config import Settings
from src.rag_core.embeddings import FastEmbedEmbeddings
from src.rag_core.generator import Generator, OpenRouterLLM
from src.rag_core.pipeline import SimpleRAG
from src.rag_core.rerankers import CrossEncoderReranker
from src.rag_core.retriever import HybridRetriever
from src.rag_core.vectorstore_qdrant import QdrantVectorStore
from src.rag_core.bm25_qdrant import BM25QdrantClient


@lru_cache
def get_settings():
    """Get application settings with caching.
    
    Returns:
        Settings instance loaded from environment variables
    """
    return Settings()


def get_rag():
    """Get configured RAG pipeline instance.
    
    Returns:
        SimpleRAG instance with configured components
        
    Note:
        Uses OpenRouter LLM if API key is provided, otherwise DummyLLM
    """
    s = get_settings()
    emb = FastEmbedEmbeddings(s.embedding_model)
    vs = QdrantVectorStore(s.qdrant_url)
    bm25 = BM25QdrantClient(s.qdrant_url)
    rr = CrossEncoderReranker(s.reranker_model)
    retr = HybridRetriever(
        bm25=bm25, vs=vs, reranker=rr, alpha=0.5
    )
    
    # Use OpenRouter if API key is provided, otherwise use DummyLLM
    if s.openrouter_api_key:
        llm = OpenRouterLLM(s.openrouter_model)
        generator = Generator(emb, llm)
        return SimpleRAG(emb, retr, generator)
    else:
        return SimpleRAG(emb, retr)
