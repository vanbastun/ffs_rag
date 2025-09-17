import json
from collections.abc import Iterable
from typing import Any, Protocol

from .openrouter_client import chat_with_openrouter


class LLMProtocol(Protocol):
    """Protocol for LLM implementations."""

    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        ...


class DummyLLM:
    """Simple LLM stub that returns fixed JSON."""

    def generate(self, prompt: str) -> str:
        """Generate dummy response.

        Args:
            prompt: Input prompt (ignored)

        Returns:
            Fixed JSON response string
        """
        return json.dumps({"answer": "I don't know", "citations": [], "confidence": 0.0})


class OpenRouterLLM:
    """OpenRouter LLM implementation."""

    def __init__(self, model: str = "deepseek/deepseek-r1-0528:free"):
        """Initialize OpenRouter LLM.

        Args:
            model: OpenRouter model name
        """
        self.model = model

    def generate(self, prompt: str) -> str:
        """Generate response using OpenRouter API.

        Args:
            prompt: Input prompt for the model

        Returns:
            Generated response string or error JSON
        """
        try:
            response = chat_with_openrouter(prompt, self.model)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return json.dumps(
                {
                    "answer": f"OpenRouter API error: {e!s}",
                    "citations": [],
                    "confidence": 0.0,
                    "error": str(e),
                }
            )


class Generator:
    """
    Answer generator for RAG.

    Args:
        embedder: Object with encode_one(str) -> vector
        llm: Object with generate(prompt:str) -> str (JSON)
    """

    def __init__(self, embedder: Any, llm: LLMProtocol | None = None):
        """Initialize RAG generator.

        Args:
            embedder: Embedding model for query encoding
            llm: Language model for generation (default: DummyLLM)
        """
        self.embedder = embedder
        self.llm = llm or DummyLLM()

    def embed_query(self, q: str) -> Any:
        """Encode query into vector.

        Args:
            q: Query string to encode

        Returns:
            Vector representation of the query
        """
        return self.embedder.encode_one(q)

    def compress(self, hits: list, budget: int = 6000) -> list:
        """Compress document list to character limit.

        Args:
            hits: List of (text, metadata, score) tuples
            budget: Maximum character budget

        Returns:
            Compressed list of hits within budget

        Note:
            Simple version - truncate texts.
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
        """Send request to LLM and return dictionary.

        Args:
            prompt: Formatted prompt for the LLM

        Returns:
            Dictionary with answer, citations, confidence, and optional error

        Note:
            Handles parsing errors gracefully.
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
        """Simulate streaming: yield response chunks.

        Args:
            prompt: Formatted prompt for the LLM

        Yields:
            Response chunks as JSON strings or parsed objects

        Note:
            Currently simulates streaming behavior.
        """
        try:
            # In real implementation, LLM connection with chunks will be here
            chunk = {"delta": "..."}
            yield json.dumps(chunk)  # string
            # Or for convenience:
            # yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)})
