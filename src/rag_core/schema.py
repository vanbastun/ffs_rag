from pydantic import BaseModel, Field


# ===== Запрос от пользователя =====
class Query(BaseModel):
    """Запрос в RAG-пайплайн."""

    question: str = Field(..., description="Текст вопроса пользователя")
    top_k: int = Field(5, ge=1, le=50, description="Сколько документов вернуть из поиска")


# ===== Документ из хранилища =====
class Document(BaseModel):
    """Документ, найденный поиском или векторной БД."""

    id: str
    content: str
    score: float = Field(..., ge=0, description="Релевантность (чем выше, тем лучше)")
    metadata: dict[str, str] = Field(default_factory=dict)


# ===== Ответ модели =====
class Answer(BaseModel):
    """Ответ, сгенерированный LLM с поддержкой источников."""

    answer_text: str
    sources: list[Document] = Field(default_factory=list)


# ===== Конфиг для эмбеддингов =====
class EmbeddingConfig(BaseModel):
    """Параметры генерации векторных представлений."""

    model_name: str = "text-embedding-3-small"
    dimension: int | None = None


# ===== Конфиг для поиска =====
class RetrieverConfig(BaseModel):
    """Параметры поиска по векторной БД."""

    index_name: str = "default"
    similarity_threshold: float = Field(0.75, ge=0.0, le=1.0)


# ===== Конфиг LLM =====
class LLMConfig(BaseModel):
    """Настройки Large Language Model."""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(1024, ge=1)


# ===== Результат поиска =====
class RetrievalResult(BaseModel):
    """Результат работы ретривера."""

    query: Query
    documents: list[Document]


# ===== Итог работы пайплайна =====
class PipelineResponse(BaseModel):
    """Финальный объект, возвращаемый API."""

    query: Query
    answer: Answer
    retrieved_docs: list[Document]
