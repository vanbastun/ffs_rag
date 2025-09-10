from typing import Any

import numpy as np
from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    def __init__(self, model_name: str, lazy: bool = False, device: str | None = None):
        """
        model_name : имя модели CrossEncoder
        lazy       : отложенная загрузка модели (True — загрузка при первом вызове rerank)
        device     : 'cpu', 'cuda' и т.д. (по умолчанию выбирается автоматически)
        """
        self.model_name = model_name
        self.device = device
        self.model: CrossEncoder | None = None
        if not lazy:
            self._load_model()

    def _load_model(self):
        if self.model is None:
            self.model = CrossEncoder(self.model_name, device=self.device)

    def rerank(
        self, query: str, candidates: list[tuple[str, Any]], return_scores: bool = False
    ) -> list:
        """
        query        : запрос (строка)
        candidates   : список кортежей вида (текст документа, метаинфо)
        return_scores: вернуть ли список кортежей (док, мета, скор) вместо чистого списка кандидатов
        """
        if not candidates:
            return []

        self._load_model()

        texts = [c[0] for c in candidates]
        pairs = [(query, text) for text in texts]

        # Получаем скор для каждого кандидата
        scores = np.array(self.model.predict(pairs), dtype=np.float32)

        # Сортируем по убыванию скоринга
        order = np.argsort(-scores)

        if return_scores:
            return [(candidates[i][0], candidates[i][1], float(scores[i])) for i in order]
        else:
            return [candidates[i] for i in order]
