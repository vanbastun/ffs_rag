"""RAG Core - Main RAG pipeline components."""

from .config import Settings
from .schema import Query, Document, Answer, PipelineResponse
from .pipeline import SimpleRAG

# Import from submodules
from .storage import BM25QdrantClient, QdrantVectorStore
from .retrieval import HybridRetriever, CrossEncoderReranker
from .generation import DummyLLM, Generator, chat_with_openrouter, build_json_prompt
from .embeddings import FastEmbedEmbeddings
from .processing import TextChunker, PIIMasker
from .observability import CacheManager, metrics_endpoint, rag_errors, rag_latency, rag_requests

__all__ = [
    # Core
    "Settings",
    "Query", 
    "Document", 
    "Answer",
    "PipelineResponse",
    "SimpleRAG",
    # Storage
    "BM25QdrantClient",
    "QdrantVectorStore", 
    # Retrieval
    "HybridRetriever",
    "CrossEncoderReranker",
    # Generation
    "DummyLLM",
    "Generator", 
    "chat_with_openrouter",
    "build_json_prompt",
    # Embeddings
    "FastEmbedEmbeddings",
    # Processing
    "TextChunker",
    "PIIMasker",
    # Observability
    "CacheManager",
    "metrics_endpoint",
    "rag_errors", 
    "rag_latency",
    "rag_requests",
]
