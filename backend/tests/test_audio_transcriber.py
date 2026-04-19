from __future__ import annotations

import wave

from app.pipelines import audio_transcriber


class Segment:
    def __init__(self, text: str):
        self.text = text


class FakeWhisper:
    def transcribe(self, path: str):
        return [Segment("test one two three")], None


def test_transcribe_contains_test(tmp_path, monkeypatch):
    path = tmp_path / "sample.wav"
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(16000)
        handle.writeframes(bytes([0, 0]) * 160)
    monkeypatch.setattr(audio_transcriber, "_load", lambda: FakeWhisper())
    transcript = audio_transcriber.transcribe(str(path))
    assert "test" in transcript.lower()
