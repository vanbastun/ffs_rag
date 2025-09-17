"""RAG Core - Main RAG pipeline components."""

from .config import Settings
from .embeddings import FastEmbedEmbeddings
from .generation import DummyLLM, Generator, OpenRouterLLM, build_json_prompt, chat_with_openrouter
from .observability import TwoLevelCache, metrics_endpoint, rag_errors, rag_latency, rag_requests
from .pipeline import SimpleRAG
from .processing import fixed_chunk, redact_pii, simple_md_clean
from .retrieval import CrossEncoderReranker, HybridRetriever
from .schema import Answer, Document, PipelineResponse, Query

# Import from submodules
from .storage import BM25QdrantClient, QdrantVectorStore

__all__ = [
    "Answer",
    # Storage
    "BM25QdrantClient",
    "CrossEncoderReranker",
    "Document",
    # Generation
    "DummyLLM",
    # Embeddings
    "FastEmbedEmbeddings",
    "Generator",
    # Retrieval
    "HybridRetriever",
    "OpenRouterLLM",
    "PipelineResponse",
    "QdrantVectorStore",
    "Query",
    # Core
    "Settings",
    "SimpleRAG",
    # Observability
    "TwoLevelCache",
    "build_json_prompt",
    "chat_with_openrouter",
    "fixed_chunk",
    "metrics_endpoint",
    "rag_errors",
    "rag_latency",
    "rag_requests",
    "redact_pii",
    # Processing
    "simple_md_clean",
]
