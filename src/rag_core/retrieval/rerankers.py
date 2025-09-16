from typing import Any

import numpy as np
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """Cross-encoder reranker for document ranking."""
    
    def __init__(self, model_name: str, lazy: bool = False, device: str | None = None):
        """Initialize CrossEncoder reranker.
        
        Args:
            model_name: CrossEncoder model name
            lazy: Lazy model loading (load on first rerank call)
            device: Device to use ('cpu', 'cuda', etc.)
        """
        self.model_name = model_name
        self.device = device
        self.model: CrossEncoder | None = None
        if not lazy:
            self._load_model()

    def _load_model(self):
        """Load CrossEncoder model if not already loaded."""
        if self.model is None:
            self.model = CrossEncoder(self.model_name, device=self.device)

    def rerank(
        self, query: str, candidates: list[tuple[str, Any]], return_scores: bool = False
    ) -> list:
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

        texts = [c[0] for c in candidates]
        pairs = [(query, text) for text in texts]

        # Get score for each candidate
        scores = np.array(self.model.predict(pairs), dtype=np.float32)

        # Sort by descending score
        order = np.argsort(-scores)

        if return_scores:
            return [(candidates[i][0], candidates[i][1], float(scores[i])) for i in order]
        else:
            return [candidates[i] for i in order]
