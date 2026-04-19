from __future__ import annotations

import os

import numpy as np

_model = None


def _load():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        cache_folder = os.getenv("MODEL_CACHE_DIR")
        _model = SentenceTransformer("BAAI/bge-small-en-v1.5", cache_folder=cache_folder)
    return _model


def embed_text(text: str) -> np.ndarray:
    vector = _load().encode(text, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32)


def embed_texts(texts: list[str]) -> np.ndarray:
    matrix = _load().encode(texts, normalize_embeddings=True, batch_size=32)
    return np.asarray(matrix, dtype=np.float32)
