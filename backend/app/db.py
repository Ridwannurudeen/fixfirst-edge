from __future__ import annotations

import math
import uuid
from collections.abc import Iterable
from typing import Any, Literal

import numpy as np

from app.config import settings

_DOC_ID_NAMESPACE = uuid.UUID("c5f04f3e-0f7c-4a10-9e6b-3fe1b3f2a6a4")

try:
    from actian_vectorai import (
        Distance,
        Field,
        FilterBuilder,
        PointStruct,
        VectorAIClient,
        VectorParams
    )
    from actian_vectorai.exceptions import UnimplementedError, VectorAIError
    from actian_vectorai.models.enums import FieldType
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local install
    Distance = Field = FilterBuilder = PointStruct = VectorAIClient = VectorParams = None
    UnimplementedError = VectorAIError = FieldType = None
    _IMPORT_ERROR: ModuleNotFoundError | None = exc
else:
    _IMPORT_ERROR = None

DocType = Literal["manual", "incident", "part", "error_code", "voice_note"]
VectorName = Literal["text_vec", "image_vec", "audio_text_vec"]

_FIELD_TYPES: dict[str, Any] = {
    "doc_type": "keyword",
    "machine_type": "keyword",
    "model_no": "keyword",
    "fault_code": "keyword",
    "severity": "keyword",
    "part_no": "keyword",
    "text_content": "text",
    "created_at": "datetime",
    "source_id": "keyword",
    "page": "integer",
    "chunk_id": "integer",
    "fix_applied": "text",
    "downtime_min": "integer",
    "parts_used": "text",
}
_COLLECTION_READY = False


def init_collection() -> None:
    _require_client()
    global _COLLECTION_READY
    if _COLLECTION_READY:
        return
    with _client() as client:
        if not client.collections.exists(settings.collection_name):
            client.collections.create(
                settings.collection_name,
                vectors_config={
                    "text_vec": VectorParams(size=384, distance=Distance.Cosine),
                    "image_vec": VectorParams(size=512, distance=Distance.Cosine),
                    "audio_text_vec": VectorParams(size=384, distance=Distance.Cosine),
                },
                on_disk_payload=True,
            )
            _ensure_field_indexes(client)
        _COLLECTION_READY = True


def upsert(
    *,
    doc_id: str,
    text_vec: np.ndarray | None,
    image_vec: np.ndarray | None,
    audio_text_vec: np.ndarray | None,
    metadata: dict,
) -> None:
    init_collection()
    vector = _build_vector_payload(text_vec, image_vec, audio_text_vec)
    payload = {**metadata, "doc_id": doc_id}
    point_id = str(uuid.uuid5(_DOC_ID_NAMESPACE, doc_id))
    point = PointStruct(id=point_id, vector=vector, payload=payload)
    with _client() as client:
        client.points.upsert(settings.collection_name, [point])


def search_text(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]:
    return _search_vector("text_vec", query_vec, filters, k)


def search_image(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]:
    return _search_vector("image_vec", query_vec, filters, k)


def search_audio(query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]:
    return _search_vector("audio_text_vec", query_vec, filters, k)


def search_hybrid(query_text: str, query_vec: np.ndarray, filters: dict | None, k: int = 10) -> list[dict]:
    init_collection()
    dense_hits = _search_vector("text_vec", query_vec, filters, 50)
    keyword_hits = _search_keyword(query_text, filters, 50)
    return _rrf_merge([dense_hits, keyword_hits], k)


def health() -> bool:
    if _IMPORT_ERROR is not None:
        return False
    try:
        with _client() as client:
            client.health_check(timeout=3.0)
        return True
    except Exception:
        return False


def _client() -> Any:
    _require_client()
    api_key = settings.actian_api_key or None
    return VectorAIClient(settings.actian_url, api_key=api_key)


def _require_client() -> None:
    if _IMPORT_ERROR is not None:
        raise RuntimeError(
            "actian-vectorai is not installed. Install backend dependencies before using the database layer."
        ) from _IMPORT_ERROR


def _ensure_field_indexes(client: Any) -> None:
    if FieldType is None or UnimplementedError is None or VectorAIError is None:
        return
    for field_name, field_type in _field_index_specs():
        try:
            client.points.create_field_index(
                settings.collection_name,
                field_name=field_name,
                field_type=field_type,
            )
        except (UnimplementedError, VectorAIError):
            continue


def _field_index_specs() -> list[tuple[str, Any]]:
    if FieldType is None:
        return []
    return [
        ("doc_type", FieldType.FieldTypeKeyword),
        ("machine_type", FieldType.FieldTypeKeyword),
        ("model_no", FieldType.FieldTypeKeyword),
        ("fault_code", FieldType.FieldTypeKeyword),
        ("severity", FieldType.FieldTypeKeyword),
        ("part_no", FieldType.FieldTypeKeyword),
        ("text_content", FieldType.FieldTypeText),
        ("created_at", FieldType.FieldTypeDatetime),
        ("source_id", FieldType.FieldTypeKeyword),
        ("page", FieldType.FieldTypeInteger),
        ("chunk_id", FieldType.FieldTypeInteger),
        ("fix_applied", FieldType.FieldTypeText),
        ("downtime_min", FieldType.FieldTypeInteger),
    ]


def _build_vector_payload(
    text_vec: np.ndarray | None,
    image_vec: np.ndarray | None,
    audio_text_vec: np.ndarray | None,
) -> dict[str, list[float]]:
    payload: dict[str, list[float]] = {}
    if text_vec is not None:
        payload["text_vec"] = _vector_to_list(text_vec)
    if image_vec is not None:
        payload["image_vec"] = _vector_to_list(image_vec)
    if audio_text_vec is not None:
        payload["audio_text_vec"] = _vector_to_list(audio_text_vec)
    if not payload:
        raise ValueError("At least one vector is required for upsert")
    return payload


def _vector_to_list(vector: np.ndarray) -> list[float]:
    return np.asarray(vector, dtype=np.float32).tolist()


def _search_vector(vector_name: VectorName, query_vec: np.ndarray, filters: dict | None, k: int) -> list[dict]:
    init_collection()
    with _client() as client:
        results = client.points.search(
            settings.collection_name,
            vector=_vector_to_list(query_vec),
            using=vector_name,
            filter=_build_filter(filters),
            limit=k,
            with_payload=True,
        )
    return [_to_hit(result) for result in results]


def _search_keyword(query_text: str, filters: dict | None, k: int) -> list[dict]:
    init_collection()
    tokens = _tokenize(query_text)
    if not tokens:
        return []
    points = _scroll_points(filters)
    if not points:
        return []
    doc_count = len(points)
    document_frequency: dict[str, int] = {}
    for point in points:
        content_tokens = set(_tokenize(_payload(point).get("text_content", "")))
        for token in tokens:
            if token in content_tokens:
                document_frequency[token] = document_frequency.get(token, 0) + 1

    hits: list[dict] = []
    for point in points:
        payload = _payload(point)
        content_tokens = _tokenize(payload.get("text_content", ""))
        if not content_tokens:
            continue
        score = 0.0
        for token in tokens:
            term_frequency = content_tokens.count(token)
            if term_frequency == 0:
                continue
            inverse_document_frequency = math.log((doc_count + 1) / (document_frequency.get(token, 0) + 1)) + 1.0
            score += term_frequency * inverse_document_frequency
        if score == 0.0:
            continue
        score /= 1.0 + math.log(len(content_tokens) + 1)
        hits.append({"id": str(point.id), "score": float(score), "metadata": payload})
    hits.sort(key=lambda item: item["score"], reverse=True)
    return hits[:k]


def _scroll_points(filters: dict | None) -> list[Any]:
    collected: list[Any] = []
    offset: str | int | None = None
    built_filter = _build_filter(filters)
    with _client() as client:
        while True:
            points, next_offset = client.points.scroll(
                settings.collection_name,
                offset=offset,
                filter=built_filter,
                limit=64,
                with_payload=True,
            )
            collected.extend(points)
            if next_offset is None:
                break
            offset = next_offset
    return collected


def _build_filter(filters: dict | None) -> Any:
    if not filters:
        return None
    builder = FilterBuilder()
    for key, value in filters.items():
        if value is None:
            continue
        field_type = _FIELD_TYPES.get(key, "keyword")
        field = Field(key)
        if field_type == "integer":
            builder.must(field.eq(int(value)))
        elif field_type == "datetime":
            builder.must(field.eq(str(value)))
        else:
            builder.must(field.eq(value))
    return builder.build()


def _payload(point: Any) -> dict[str, Any]:
    payload = getattr(point, "payload", None)
    return payload if isinstance(payload, dict) else {}


def _to_hit(result: Any) -> dict[str, Any]:
    payload = _payload(result)
    return {
        "id": str(payload.get("doc_id") or getattr(result, "id")),
        "score": float(getattr(result, "score", 0.0)),
        "metadata": payload,
    }


def _tokenize(text: str) -> list[str]:
    return [token for token in "".join(char.lower() if char.isalnum() else " " for char in text).split() if token]


def _rrf_merge(rankings: Iterable[list[dict]], k: int) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for ranking in rankings:
        for index, item in enumerate(ranking, start=1):
            item_id = str(item["id"])
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (60 + index)
            payloads[item_id] = item
    merged = [
        {"id": item_id, "score": score, "metadata": payloads[item_id]["metadata"]}
        for item_id, score in scores.items()
    ]
    merged.sort(key=lambda item: item["score"], reverse=True)
    return merged[:k]
