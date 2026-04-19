from __future__ import annotations

from pathlib import Path

try:
    import pdfplumber
except ModuleNotFoundError:
    pdfplumber = None


def chunk_pdf(path: str, target_tokens: int = 400, overlap: int = 50) -> list[dict[str, int | str]]:
    if pdfplumber is None:
        raise ModuleNotFoundError("pdfplumber is required")
    chunks: list[dict[str, int | str]] = []
    words_per_chunk = max(1, int(target_tokens / 1.3))
    overlap_words = max(0, int(overlap / 1.3))
    source = Path(path).name
    chunk_id = 0

    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            words = text.split()
            start = 0
            while start < len(words):
                end = min(len(words), start + words_per_chunk)
                chunk_text = " ".join(words[start:end]).strip()
                if chunk_text:
                    chunks.append(
                        {
                            "text": chunk_text,
                            "page": page_number,
                            "chunk_id": chunk_id,
                            "source": source,
                        }
                    )
                    chunk_id += 1
                if end >= len(words):
                    break
                start = max(end - overlap_words, start + 1)
    return chunks
