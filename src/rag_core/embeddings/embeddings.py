from typing import Any

import numpy as np
from fastembed import TextEmbedding


class FastEmbedEmbeddings:
    """FastEmbed wrapper for convenient embedding generation.

    Provides normalization and support for both lists and single strings.
    """

    def __init__(self, model_name: str = "jinaai/jina-embeddings-v2-small-en"):
        """Initialize FastEmbed embeddings.

        Args:
            model_name: FastEmbed model name
        """
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)

    def encode(self, texts: str | list[str], normalize: bool = True, **kwargs: Any) -> np.ndarray:
        """Encode text(s) into embeddings.

        Args:
            texts: String or list of strings to encode
            normalize: Whether to normalize vectors (L2 norm)
            **kwargs: Additional options passed to model.embed

        Returns:
            Numpy array of embeddings
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

    def encode_one(self, text: str, normalize: bool = True, **kwargs: Any) -> np.ndarray:
        """Encode single string and return vector.

        Args:
            text: Single string to encode
            normalize: Whether to normalize vector (L2 norm)
            **kwargs: Additional options passed to model.embed

        Returns:
            Single embedding vector
        """
        return self.encode(text, normalize=normalize, **kwargs)[0]
