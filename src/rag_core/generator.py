import json
from collections.abc import Iterable
from typing import Any


class DummyLLM:
    """Простая заглушка LLM — возвращает фиксированный JSON."""

    def generate(self, prompt: str) -> str:
        return json.dumps({"answer": "I don't know", "citations": [], "confidence": 0.0})


class Generator:
    """
    Генератор ответов для RAG.
    embedder: объект с методом encode_one(str) -> вектор
    llm: объект с методом generate(prompt:str) -> str (JSON)
    """

    def __init__(self, embedder: Any, llm: DummyLLM | None = None):
        self.embedder = embedder
        self.llm = llm or DummyLLM()

    def embed_query(self, q: str) -> Any:
        """Энкодинг запроса в вектор."""
        return self.embedder.encode_one(q)

    def compress(self, hits: list, budget: int = 6000) -> list:
        """
        Сжать список документов до лимита символов.
        Пока простая версия — обрезаем тексты.
        """
        result = []
        total = 0
        for h in hits:
            text = h[0]
            if total + len(text) > budget:
                break
            result.append(h)
            total += len(text)
        return result

    def generate(self, prompt: str) -> dict[str, Any]:
        """
        Отправить запрос в LLM и вернуть словарь.
        Обработка ошибок парсинга.
        """
        try:
            raw = self.llm.generate(prompt)
            return json.loads(raw)
        except json.JSONDecodeError as e:
            return {
                "answer": "LLM output parsing error",
                "citations": [],
                "confidence": 0.0,
                "error": str(e),
            }
        except Exception as e:
            return {
                "answer": "Generation error",
                "citations": [],
                "confidence": 0.0,
                "error": str(e),
            }

    def stream_generate(self, prompt: str) -> Iterable[str | dict[str, Any]]:
        """
        Имитация стриминга: выдаём порции ответа.
        Можно вернуть как строки JSON, так и уже распарсенные объекты.
        """
        try:
            # В реальной реализации тут будет подключение к LLM с чанками
            chunk = {"delta": "..."}
            yield json.dumps(chunk)  # строка
            # Или для удобства:
            # yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)})
