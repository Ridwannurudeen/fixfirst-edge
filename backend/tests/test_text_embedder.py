from __future__ import annotations

import numpy as np

from app.pipelines import text_embedder


class FakeModel:
    def encode(self, value, normalize_embeddings: bool = True, batch_size: int | None = None):
        if isinstance(value, list):
            return np.ones((len(value), 384), dtype=np.float32)
        return np.ones(384, dtype=np.float32)


def test_embed_text_shape(monkeypatch):
    monkeypatch.setattr(text_embedder, "_load", lambda: FakeModel())
    vector = text_embedder.embed_text("motor overload")
    assert vector.shape == (384,)


def test_embed_texts_shape(monkeypatch):
    monkeypatch.setattr(text_embedder, "_load", lambda: FakeModel())
    matrix = text_embedder.embed_texts(["one", "two"])
    assert matrix.shape == (2, 384)
