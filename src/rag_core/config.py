from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    redis_url: str = "redis://localhost:6379/0"
    embedding_model: str = "jinaai/jina-embeddings-v2-small-en"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-r1-0528:free"

    class Config:
        env_prefix = "RAG_"
        env_file = ".env"
