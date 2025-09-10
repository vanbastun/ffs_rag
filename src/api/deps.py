from functools import lru_cache

from src.rag_core.config import Settings
from src.rag_core.embeddings import FastEmbedEmbeddings
from src.rag_core.pipeline import SimpleRAG
from src.rag_core.rerankers import CrossEncoderReranker
from src.rag_core.retriever import HybridRetriever
from src.rag_core.vectorstore_qdrant import QdrantVectorStore


@lru_cache
def get_settings():
    return Settings()


def get_rag():
    s = get_settings()
    emb = FastEmbedEmbeddings(s.embedding_model)
    vs = QdrantVectorStore(s.qdrant_url)
    rr = CrossEncoderReranker(s.reranker_model)
    retr = HybridRetriever(
        bm25=None, vs=vs, reranker=rr, alpha=0.5
    )  # нужно заполнить BM25 при инициализации
    return SimpleRAG(emb, retr)
