import time
from collections.abc import Generator as GenType
from typing import Any

from src.rag_core.generation import DummyLLM, Generator, build_json_prompt


class SimpleRAG:
    def __init__(
        self,
        embedder: Any,
        retriever: Any,
        generator: Generator | None = None,
        max_ctx_chars: int = 6000,
        debug: bool = False,
    ) -> None:
        """
        Args:
            embedder: Object with encode_one(text) -> np.ndarray
            retriever: Object with retrieve(query, qvec, k, filters) -> [(text, meta, score), ...]
            generator: LLM generator (default: DummyLLM)
            max_ctx_chars: Character limit for context in build_json_prompt
            debug: Whether to output debug info about stage timing
        """
        self.embedder = embedder
        self.retriever = retriever
        self.generator = generator or Generator(embedder, DummyLLM())
        self.max_ctx_chars = max_ctx_chars
        self.debug = debug

    def _prepare_prompt(self, q: str, k: int, filters: dict[str, Any] | None = None) -> str:
        """Prepare prompt by encoding query and retrieving relevant documents.

        Args:
            q: User question/query
            k: Number of documents to retrieve
            filters: Optional filters for retrieval

        Returns:
            Formatted prompt string ready for LLM
        """
        t0 = time.time()
        qvec = self.embedder.encode_one(q)
        if self.debug:
            print(f"[DEBUG] Encoding took {time.time() - t0:.3f}s")

        t1 = time.time()
        hits = self.retriever.retrieve(q, qvec, k=k, filters=filters)
        if self.debug:
            print(f"[DEBUG] Retrieval took {time.time() - t1:.3f}s — {len(hits)} hits")

        prompt = build_json_prompt(q, hits, max_ctx_chars=self.max_ctx_chars)
        return prompt

    def answer(self, q: str, k: int = 6, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate answer for user question using RAG pipeline.

        Args:
            q: User question/query
            k: Number of documents to retrieve (default: 6)
            filters: Optional filters for retrieval

        Returns:
            Generated answer as dictionary
        """
        prompt = self._prepare_prompt(q, k, filters)
        return self.generator.generate(prompt)

    def answer_stream(
        self, q: str, k: int = 6, filters: dict[str, Any] | None = None
    ) -> GenType[str | dict[str, Any], None, None]:
        """Generate streaming answer for user question using RAG pipeline.

        Args:
            q: User question/query
            k: Number of documents to retrieve (default: 6)
            filters: Optional filters for retrieval

        Yields:
            Streaming response chunks
        """
        prompt = self._prepare_prompt(q, k, filters)
        yield from self.generator.stream_generate(prompt)
