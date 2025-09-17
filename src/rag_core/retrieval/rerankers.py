from typing import Any

import numpy as np
from fastembed.rerank.cross_encoder import TextCrossEncoder


class CrossEncoderReranker:
    """Cross-encoder reranker for document ranking using FastEmbed."""

    def __init__(self, model_name: str, lazy: bool = True, device: str | None = None):
        """Initialize CrossEncoder reranker.

        Args:
            model_name: CrossEncoder model name (FastEmbed compatible)
            lazy: Lazy model loading (load on first rerank call) - defaults to True
            device: Device to use ('cpu', 'cuda', etc.) - ignored for FastEmbed
        """
        self.model_name = model_name
        self.device = device  # Keep for compatibility but FastEmbed handles device automatically
        self.model: TextCrossEncoder | None = None
        if not lazy:
            self._load_model()

    def _load_model(self) -> None:
        """Load FastEmbed TextCrossEncoder model if not already loaded."""
        if self.model is None:
            self.model = TextCrossEncoder(model_name=self.model_name)

    def rerank(
        self, query: str, candidates: list[tuple[str, Any]], return_scores: bool = False
    ) -> list[tuple[str, Any, float]]:
        """Rerank candidates based on query relevance.

        Args:
            query: Query string
            candidates: List of (document_text, metadata) tuples
            return_scores: Whether to return (doc, meta, score) tuples

        Returns:
            Reranked list of candidates
        """
        if not candidates:
            return []

        self._load_model()

        # Ensure all texts are strings
        texts = []
        for c in candidates:
            text = c[0]
            if not isinstance(text, str):
                text = str(text)
            texts.append(text)

        # FastEmbed rerank expects query and list of documents
        if self.model is None:
            raise RuntimeError("Model not loaded")
        scores = list(self.model.rerank(query, texts))

        # Sort by descending score
        order = np.argsort(-np.array(scores))

        if return_scores:
            return [(candidates[i][0], candidates[i][1], float(scores[i])) for i in order]
        else:
            return [candidates[i] for i in order]
