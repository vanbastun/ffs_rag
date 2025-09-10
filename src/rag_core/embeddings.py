import numpy as np
from fastembed import TextEmbedding


class FastEmbedEmbeddings:
    """
    Обёртка над FastEmbed для удобного получения эмбеддингов
    с нормализацией и поддержкой как списков, так и одиночных строк.
    """

    def __init__(self, model_name: str = "jinaai/jina-embeddings-v2-small-en"):
        """
        model_name — имя модели FastEmbed (по умолчанию jinaai/jina-embeddings-v2-small-en)
        """
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)

    def encode(self, texts: str | list[str], normalize: bool = True, **kwargs) -> np.ndarray:
        """
        Кодирует текст(ы) в эмбеддинги.
        texts     — строка или список строк
        normalize — нормализовать ли вектора (L2-норма)
        kwargs    — проброс опций в self.model.embed (batch_size и т.п.)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = list(self.model.embed(texts, **kwargs))
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        if normalize:
            # L2 normalization
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            embeddings_array = embeddings_array / (norms + 1e-8)
        
        return embeddings_array

    def encode_one(self, text: str, normalize: bool = True, **kwargs) -> np.ndarray:
        """Кодирует одну строку и возвращает вектор."""
        return self.encode(text, normalize=normalize, **kwargs)[0]
