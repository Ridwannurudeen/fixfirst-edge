from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from app import db
from app.pipelines.audio_transcriber import transcribe
from app.pipelines.identifier_extractor import fill_identifier_fields
from app.pipelines.image_embedder import embed_image
from app.pipelines.pdf_chunker import chunk_pdf
from app.pipelines.text_embedder import embed_text


async def ingest_manual(file: UploadFile, machine_type: str, model_no: str) -> int:
    temp_path = await _save_upload(file)
    try:
        db.init_collection()
        chunks = chunk_pdf(str(temp_path))
        for chunk in chunks:
            metadata = _base_metadata("manual", machine_type, model_no=model_no)
            chunk_text = str(chunk["text"])
            metadata.update(
                {
                    "text_content": chunk_text,
                    "source_id": file.filename or temp_path.name,
                    "page": int(chunk["page"]),
                    "chunk_id": int(chunk["chunk_id"]),
                }
            )
            fill_identifier_fields(metadata, chunk_text)
            doc_id = f"manual:{metadata['source_id']}:{metadata['page']}:{metadata['chunk_id']}"
            db.upsert(
                doc_id=doc_id,
                text_vec=embed_text(chunk_text),
                image_vec=None,
                audio_text_vec=None,
                metadata=metadata,
            )
        return len(chunks)
    finally:
        temp_path.unlink(missing_ok=True)


def ingest_incident(row: dict[str, str | int | float | bool | None]) -> str:
    db.init_collection()
    if _is_error_code_row(row):
        return _ingest_error_code(row)

    source_id = str(row.get("id") or f"incident-{_timestamp_slug()}")
    metadata = _base_metadata(
        "incident",
        str(row.get("machine_type") or ""),
        model_no=_string_or_none(row.get("model_no")),
        fault_code=_string_or_none(row.get("fault_code")),
        severity=_string_or_none(row.get("severity")),
        part_no=_string_or_none(row.get("part_no")),
    )
    text_content = " ".join(
        part
        for part in [
            _string_or_none(row.get("symptom")),
            _string_or_none(row.get("fault_code")),
            _string_or_none(row.get("fix_applied")),
            _string_or_none(row.get("parts_used")),
        ]
        if part
    )
    metadata.update(
        {
            "text_content": text_content,
            "source_id": source_id,
            "page": None,
            "chunk_id": None,
            "fix_applied": _string_or_none(row.get("fix_applied")),
            "downtime_min": _int_or_none(row.get("downtime_min")),
            "parts_used": _string_or_none(row.get("parts_used")),
            "verified": _bool_or_default(row.get("verified"), False),
        }
    )
    fill_identifier_fields(metadata, text_content)
    doc_id = f"incident:{source_id}"
    db.upsert(
        doc_id=doc_id,
        text_vec=embed_text(text_content),
        image_vec=None,
        audio_text_vec=None,
        metadata=metadata,
    )
    return doc_id


async def ingest_image(
    file: UploadFile,
    machine_type: str,
    fault_code: str | None,
    severity: str | None,
) -> str:
    temp_path = await _save_upload(file)
    try:
        db.init_collection()
        text_content = " ".join(part for part in [machine_type, fault_code, severity, file.filename or temp_path.name] if part)
        source_id = file.filename or temp_path.name
        metadata = _base_metadata(
            "incident",
            machine_type,
            fault_code=fault_code,
            severity=severity,
        )
        metadata.update(
            {
                "text_content": text_content,
                "source_id": source_id,
                "page": None,
                "chunk_id": None,
                "fix_applied": None,
                "downtime_min": None,
                "parts_used": None,
            }
        )
        fill_identifier_fields(metadata, text_content)
        doc_id = f"image:{source_id}"
        db.upsert(
            doc_id=doc_id,
            text_vec=embed_text(text_content),
            image_vec=embed_image(str(temp_path)),
            audio_text_vec=None,
            metadata=metadata,
        )
        return doc_id
    finally:
        temp_path.unlink(missing_ok=True)


async def ingest_voice(file: UploadFile, machine_type: str) -> str:
    temp_path = await _save_upload(file)
    try:
        db.init_collection()
        transcript = transcribe(str(temp_path))
        source_id = file.filename or temp_path.name
        metadata = _base_metadata("voice_note", machine_type)
        metadata.update(
            {
                "text_content": transcript,
                "source_id": source_id,
                "page": None,
                "chunk_id": None,
                "fix_applied": None,
                "downtime_min": None,
                "parts_used": None,
            }
        )
        fill_identifier_fields(metadata, transcript)
        doc_id = f"voice:{source_id}"
        db.upsert(
            doc_id=doc_id,
            text_vec=None,
            image_vec=None,
            audio_text_vec=embed_text(transcript),
            metadata=metadata,
        )
        return doc_id
    finally:
        temp_path.unlink(missing_ok=True)


def ingest_part(row: dict[str, str | int | float | bool | None]) -> str:
    db.init_collection()
    part_no = str(row.get("part_no") or f"part-{_timestamp_slug()}")
    name = _string_or_none(row.get("name")) or "Unknown Part"
    model_no = _string_or_none(row.get("model_no"))
    metadata = _base_metadata(
        "part",
        str(row.get("machine_type") or ""),
        model_no=model_no,
        part_no=part_no,
    )
    text_content = " ".join(
        part
        for part in [
            part_no,
            name,
            _string_or_none(row.get("description")),
            _string_or_none(row.get("machine_type")),
            model_no,
        ]
        if part
    )
    metadata.update(
        {
            "text_content": text_content,
            "source_id": part_no,
            "page": None,
            "chunk_id": None,
            "fix_applied": None,
            "downtime_min": None,
            "parts_used": None,
            "name": name,
        }
    )
    fill_identifier_fields(metadata, text_content)
    doc_id = f"part:{part_no}"
    db.upsert(
        doc_id=doc_id,
        text_vec=embed_text(text_content),
        image_vec=None,
        audio_text_vec=None,
        metadata=metadata,
    )
    return doc_id


async def _save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(await file.read())
        return Path(handle.name)


def _base_metadata(
    doc_type: str,
    machine_type: str,
    *,
    model_no: str | None = None,
    fault_code: str | None = None,
    severity: str | None = None,
    part_no: str | None = None,
) -> dict[str, str | int | bool | None]:
    return {
        "doc_type": doc_type,
        "machine_type": machine_type,
        "model_no": model_no,
        "fault_code": fault_code,
        "severity": severity,
        "part_no": part_no,
        "text_content": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_id": "",
        "page": None,
        "chunk_id": None,
        "fix_applied": None,
        "downtime_min": None,
        "parts_used": None,
        "verified": False,
    }


def _ingest_error_code(row: dict[str, str | int | float | bool | None]) -> str:
    source_id = str(row.get("fault_code") or f"error-code-{_timestamp_slug()}")
    description = _string_or_none(row.get("description")) or ""
    metadata = _base_metadata(
        "error_code",
        str(row.get("machine_type") or ""),
        fault_code=_string_or_none(row.get("fault_code")),
        severity=_string_or_none(row.get("severity")),
        part_no=_string_or_none(row.get("part_no")),
    )
    metadata.update(
        {
            "text_content": " ".join(part for part in [metadata.get("fault_code"), description] if part),
            "source_id": source_id,
            "page": None,
            "chunk_id": None,
            "fix_applied": None,
            "downtime_min": None,
            "parts_used": None,
            "verified": _bool_or_default(row.get("verified"), False),
        }
    )
    fill_identifier_fields(metadata, str(metadata["text_content"]))
    doc_id = f"error_code:{source_id}"
    db.upsert(
        doc_id=doc_id,
        text_vec=embed_text(str(metadata["text_content"])),
        image_vec=None,
        audio_text_vec=None,
        metadata=metadata,
    )
    return doc_id


def _is_error_code_row(row: dict[str, str | int | float | bool | None]) -> bool:
    return bool(row.get("fault_code")) and row.get("description") is not None and row.get("symptom") is None


def _string_or_none(value: str | int | float | bool | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: str | int | float | bool | None) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _bool_or_default(value: str | int | float | bool | None, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    return default
