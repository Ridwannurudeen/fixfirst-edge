from __future__ import annotations

import base64

import numpy as np

from app.pipelines import image_embedder

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a4e0AAAAASUVORK5CYII="
)


class FakeModel:
    def encode(self, value, normalize_embeddings: bool = True, batch_size: int | None = None):
        if isinstance(value, list):
            return np.ones((len(value), 512), dtype=np.float32)
        return np.ones(512, dtype=np.float32)


def test_embed_image_shape(tmp_path, monkeypatch):
    path = tmp_path / "sample.png"
    path.write_bytes(PNG_BYTES)
    monkeypatch.setattr(image_embedder, "_load", lambda: FakeModel())
    vector = image_embedder.embed_image(str(path))
    assert vector.shape == (512,)


def test_embed_images_shape(tmp_path, monkeypatch):
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(PNG_BYTES)
    second.write_bytes(PNG_BYTES)
    monkeypatch.setattr(image_embedder, "_load", lambda: FakeModel())
    matrix = image_embedder.embed_images([str(first), str(second)])
    assert matrix.shape == (2, 512)
