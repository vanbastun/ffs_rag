import time
from collections.abc import Generator as GenType
from typing import Any

from src.rag_core.generator import DummyLLM, Generator
from src.rag_core.prompting import build_json_prompt


class SimpleRAG:
    def __init__(
        self,
        embedder,
        retriever,
        generator: Generator | None = None,
        max_ctx_chars: int = 6000,
        debug: bool = False,
    ):
        """
        embedder     — объект с методом encode_one(text) -> np.ndarray
        retriever    — объект с методом retrieve(query, qvec, k, filters) -> [(text, meta, score), ...]
        generator    — LLM-генератор (по умолчанию DummyLLM)
        max_ctx_chars — лимит символов контекста для build_json_prompt
        debug        — выводить ли отладочную инфу по времени этапов
        """
        self.embedder = embedder
        self.retriever = retriever
        self.generator = generator or Generator(embedder, DummyLLM())
        self.max_ctx_chars = max_ctx_chars
        self.debug = debug

    def _prepare_prompt(self, q: str, k: int, filters: dict[str, Any] | None = None) -> str:
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

    def answer(self, q: str, k: int = 6, filters: dict[str, Any] | None = None) -> str:
        prompt = self._prepare_prompt(q, k, filters)
        return self.generator.generate(prompt)

    def answer_stream(
        self, q: str, k: int = 6, filters: dict[str, Any] | None = None
    ) -> GenType[str, None, None]:
        prompt = self._prepare_prompt(q, k, filters)
        yield from self.generator.stream_generate(prompt)
