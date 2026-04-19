from __future__ import annotations

import os
from pathlib import Path

_model = None


def _load():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        cache_root = os.getenv("MODEL_CACHE_DIR")
        download_root = str(Path(cache_root) / "whisper") if cache_root else None
        _model = WhisperModel("tiny.en", device="cpu", compute_type="int8", download_root=download_root)
    return _model


def transcribe(path: str) -> str:
    segments, _ = _load().transcribe(path)
    text = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
    return text.strip()
