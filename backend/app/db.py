from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Any, Literal

import numpy as np

from app.config import settings
from app.pipelines.identifier_extractor import extract_identifiers

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
    "verified": "boolean",
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
    identifier_hits = _search_identifier_branch(query_text, query_vec, filters, 50)
    rankings: list[tuple[float, list[dict]]] = [(1.0, dense_hits)]
    if identifier_hits:
        rankings.append((2.0, identifier_hits))
    return _rrf_merge(rankings, k)


def health() -> bool:
    if _IMPORT_ERROR is not None:
        return False
    try:
        with _client() as client:
            client.health_check(timeout=3.0)
        return True
    except Exception:
        return False


def collection_ready() -> bool:
    if _IMPORT_ERROR is not None:
        return False
    try:
        with _client() as client:
            return bool(client.collections.exists(settings.collection_name))
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
        ("verified", FieldType.FieldTypeBool),
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


def _search_identifier_branch(query_text: str, query_vec: np.ndarray, filters: dict | None, k: int) -> list[dict]:
    # Identifier extraction keeps the second retrieval branch inside Actian by
    # promoting exact fault/model/part matches through metadata filters.
    identifiers = {key: value for key, value in extract_identifiers(query_text).items() if value}
    if not identifiers:
        return []

    rankings: list[list[dict]] = []
    candidate_filters = _identifier_filters(identifiers)
    for extra_filters in candidate_filters:
        rankings.append(_search_vector("text_vec", query_vec, _merge_filters(filters, extra_filters), k))
    return _rrf_merge(rankings, k)


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
        elif field_type == "boolean":
            builder.must(field.eq(bool(value)))
        else:
            builder.must(field.eq(value))
    return builder.build()


def _identifier_filters(identifiers: dict[str, str]) -> list[dict[str, str]]:
    # Only emit filter branches specific enough to justify an RRF boost.
    # Combined (>1 identifier) and fault_code-alone are high-signal; a bare
    # model_no or part_no is too broad and would dilute the fused ranking.
    rankings: list[dict[str, str]] = []
    if len(identifiers) > 1:
        rankings.append(dict(identifiers))
    fault_code = identifiers.get("fault_code")
    if fault_code:
        rankings.append({"fault_code": fault_code})
    return rankings


def _merge_filters(base: dict | None, extra: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    if base:
        merged.update(base)
    merged.update(extra)
    return merged


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


def _rrf_merge(
    rankings: Iterable[list[dict] | tuple[float, list[dict]]],
    k: int,
) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for entry in rankings:
        if isinstance(entry, tuple):
            weight, ranking = entry
        else:
            weight, ranking = 1.0, entry
        for index, item in enumerate(ranking, start=1):
            item_id = str(item["id"])
            scores[item_id] = scores.get(item_id, 0.0) + weight / (60 + index)
            payloads[item_id] = item
    merged = [
        {"id": item_id, "score": score, "metadata": payloads[item_id]["metadata"]}
        for item_id, score in scores.items()
    ]
    merged.sort(key=lambda item: item["score"], reverse=True)
    return merged[:k]
