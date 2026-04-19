from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image

_model = None


def _load():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        cache_folder = os.getenv("MODEL_CACHE_DIR")
        _model = SentenceTransformer("clip-ViT-B-32", cache_folder=cache_folder)
    return _model


def embed_image(path: str) -> np.ndarray:
    with Image.open(Path(path)) as opened:
        image = opened.convert("RGB")
        vector = _load().encode(image, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32)


def embed_images(paths: list[str]) -> np.ndarray:
    images = []
    for path in paths:
        with Image.open(Path(path)) as opened:
            images.append(opened.convert("RGB"))
    matrix = _load().encode(images, normalize_embeddings=True, batch_size=16)
    return np.asarray(matrix, dtype=np.float32)
