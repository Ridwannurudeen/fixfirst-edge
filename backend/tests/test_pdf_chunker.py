from __future__ import annotations

from app.pipelines import pdf_chunker


class FakePage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self) -> str:
        return self._text


class FakePdf:
    def __init__(self, pages: list[FakePage]):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None


class FakePdfPlumber:
    @staticmethod
    def open(path: str):
        return FakePdf([FakePage("alpha beta gamma delta epsilon " * 80)])


def test_chunk_pdf_outputs_expected_fields(monkeypatch):
    monkeypatch.setattr(pdf_chunker, "pdfplumber", FakePdfPlumber())
    chunks = pdf_chunker.chunk_pdf("manual.pdf", target_tokens=40, overlap=10)
    assert chunks
    assert {"text", "page", "chunk_id", "source"} <= set(chunks[0].keys())
    assert chunks[0]["source"] == "manual.pdf"
