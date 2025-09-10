import numpy as np


class HybridRetriever:
    def __init__(self, bm25, vs, reranker=None, alpha: float = 0.5):
        """
        bm25    — объект BM25 поиска (имеет .search(query, k) → [(id, meta, score), ...])
        vs      — векторное хранилище (имеет .search(qvec, k) → [(id, meta, score), ...])
        reranker — опциональный reranker
        alpha   — вес векторного поиска (0..1)
        """
        self.bm25 = bm25
        self.vs = vs
        self.reranker = reranker
        self.alpha = alpha

    def retrieve(self, query: str, qvec: np.ndarray, k: int = 10) -> list[tuple[str, dict, float]]:
        bm25_hits = self.bm25.search(query, k=k)
        dense_hits = self.vs.search(qvec, k=k)

        bm25_scores = {doc_id: score for doc_id, _, score in bm25_hits}
        dense_scores = {doc_id: score for doc_id, _, score in dense_hits}

        if bm25_scores:
            max_bm25 = max(bm25_scores.values())
            bm25_scores = {doc_id: s / max_bm25 for doc_id, s in bm25_scores.items()}
        if dense_scores:
            max_dense = max(dense_scores.values())
            dense_scores = {doc_id: s / max_dense for doc_id, s in dense_scores.items()}

        all_ids = set(bm25_scores) | set(dense_scores)
        fused = {}
        meta_map = {}

        for doc_id in all_ids:
            bm25_s = bm25_scores.get(doc_id, 0.0)
            dense_s = dense_scores.get(doc_id, 0.0)
            fused_score = (1 - self.alpha) * bm25_s + self.alpha * dense_s
            fused[doc_id] = fused_score

            meta = next((m for i, m, _ in bm25_hits if i == doc_id), None)
            if not meta:
                meta = next((m for i, m, _ in dense_hits if i == doc_id), {})
            meta_map[doc_id] = meta

        ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
        ranked_hits = [(doc_id, meta_map[doc_id], score) for doc_id, score in ranked]

        if self.reranker:
            ranked_hits = self.reranker.rerank(query, ranked_hits)

        return ranked_hits[:k]
