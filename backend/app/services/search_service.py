from __future__ import annotations

from fastapi import UploadFile

from app import db
from app.pipelines.audio_transcriber import transcribe
from app.pipelines.identifier_extractor import extract_identifiers
from app.pipelines.image_embedder import embed_image
from app.pipelines.text_embedder import embed_text
from app.schemas import DiagnoseEvidence, DiagnoseResponse, SearchFilters
from app.services.diagnose_service import build_recommended_steps
from app.services.ingest_service import _save_upload


def search_text(query: str, filters: SearchFilters | None) -> list[dict]:
    query_vec = embed_text(query)
    return db.search_hybrid(query, query_vec, _filters(filters), k=10)


async def search_image(file: UploadFile, filters: SearchFilters | None) -> list[dict]:
    temp_path = await _save_upload(file)
    try:
        query_vec = embed_image(str(temp_path))
        return db.search_image(query_vec, _filters(filters), k=10)
    finally:
        temp_path.unlink(missing_ok=True)


async def search_voice(file: UploadFile, filters: SearchFilters | None) -> tuple[str, list[dict]]:
    temp_path = await _save_upload(file)
    try:
        transcript = transcribe(str(temp_path))
        query_vec = embed_text(transcript)
        voice_hits = db.search_audio(query_vec, _filters(filters), k=10)
        text_hits = db.search_hybrid(transcript, query_vec, _filters(filters), k=10)
        results = _rrf_merge([voice_hits, text_hits])
        return transcript, results
    finally:
        temp_path.unlink(missing_ok=True)


async def search_multimodal(
    text: str | None,
    image: UploadFile | None,
    audio: UploadFile | None,
    filters: SearchFilters | None,
) -> tuple[str | None, list[dict]]:
    rankings: list[list[dict]] = []
    transcript: str | None = None
    if text and text.strip():
        rankings.append(search_text(text.strip(), filters))
    if image is not None:
        rankings.append(await search_image(image, filters))
    if audio is not None:
        transcript, audio_results = await search_voice(audio, filters)
        rankings.append(audio_results)
    return transcript, _rrf_merge(rankings)


async def diagnose(
    query: str | None,
    image: UploadFile | None,
    voice: UploadFile | None,
    filters: SearchFilters | None,
) -> DiagnoseResponse:
    transcript: str | None = None
    image_results: list[dict] = []
    voice_results: list[dict] = []
    seed_text = query.strip() if query else ""

    if voice is not None:
        transcript, voice_results = await search_voice(voice, filters)
        if not seed_text:
            seed_text = transcript

    if image is not None:
        image_results = await search_image(image, filters)
        if not seed_text and image_results:
            seed_text = _metadata_seed(image_results[0]["metadata"])
        elif seed_text and image_results:
            image_seed = _metadata_seed(image_results[0]["metadata"])
            if image_seed:
                seed_text = f"{seed_text} {image_seed}"

    manual_section = _top_manual(seed_text, filters)
    similar_incident = _top_incident(seed_text, filters, image_results or voice_results)
    candidate_part = _top_part(seed_text, filters, similar_incident)
    recommended_steps, confidence = build_recommended_steps(manual_section, similar_incident, candidate_part)

    evidence = DiagnoseEvidence(
        manual_section=None
        if manual_section is None
        else {
            "source": str(manual_section["source"]),
            "page": manual_section["page"],
            "snippet": str(manual_section["snippet"]),
        },
        similar_incident=None
        if similar_incident is None
        else {
            "id": str(similar_incident["id"]),
            "fix_applied": str(similar_incident["fix_applied"]),
            "downtime_min": similar_incident["downtime_min"],
        },
        candidate_part=None
        if candidate_part is None
        else {
            "part_no": str(candidate_part["part_no"]),
            "name": str(candidate_part["name"]),
        },
    )
    return DiagnoseResponse(
        evidence=evidence,
        confidence=confidence,
        recommended_steps=recommended_steps,
        transcript=transcript,
    )


def _top_manual(query: str, filters: SearchFilters | None) -> dict | None:
    if not query:
        return None
    manual_query = _manual_query(query)
    manual_filters = _merged_filters(filters, {"doc_type": "manual"})
    exact_filters = _identifier_filters(query, allowed={"model_no", "fault_code"})
    if exact_filters:
        hits = db.search_hybrid(manual_query, embed_text(manual_query), {**manual_filters, **exact_filters}, k=1)
        if hits:
            return _manual_evidence(hits[0])
    hits = db.search_hybrid(manual_query, embed_text(manual_query), manual_filters, k=1)
    if not hits:
        return None
    return _manual_evidence(hits[0])


def _manual_evidence(hit: dict) -> dict:
    metadata = hit["metadata"]
    return {
        "source": metadata.get("source_id", ""),
        "page": metadata.get("page"),
        "snippet": str(metadata.get("text_content", ""))[:300],
        "score": hit["score"],
    }


def _top_incident(query: str, filters: SearchFilters | None, fallback_hits: list[dict]) -> dict | None:
    incident_filters = _merged_filters(filters, {"doc_type": "incident", "verified": True})
    if query:
        exact_filters = _identifier_filters(query)
        hits = []
        if exact_filters:
            hits = db.search_hybrid(query, embed_text(query), {**incident_filters, **exact_filters}, k=1)
        if not hits:
            hits = db.search_hybrid(query, embed_text(query), incident_filters, k=1)
    else:
        hits = [
            hit
            for hit in fallback_hits
            if hit["metadata"].get("doc_type") == "incident" and hit["metadata"].get("verified") is True
        ][:1]
    if not hits:
        return None
    metadata = hits[0]["metadata"]
    return {
        "id": str(metadata.get("source_id", hits[0]["id"])),
        "machine_id": metadata.get("model_no") or metadata.get("machine_type") or "unknown machine",
        "fix_applied": metadata.get("fix_applied") or "No fix recorded",
        "downtime_min": metadata.get("downtime_min"),
        "score": hits[0]["score"],
        "machine_type": metadata.get("machine_type"),
        "model_no": metadata.get("model_no"),
    }


def _top_part(query: str, filters: SearchFilters | None, incident: dict | None) -> dict | None:
    if not query and incident is None:
        return None
    extra_filters: dict[str, str] = {"doc_type": "part"}
    if incident:
        if incident.get("machine_type"):
            extra_filters["machine_type"] = str(incident["machine_type"])
        if incident.get("model_no"):
            extra_filters["model_no"] = str(incident["model_no"])
    part_filters = _merged_filters(filters, extra_filters)
    seed_text = query or (str(incident.get("fix_applied", "")) if incident else "")
    if not seed_text:
        return None
    hits = db.search_hybrid(seed_text, embed_text(seed_text), part_filters, k=1)
    if not hits:
        return None
    metadata = hits[0]["metadata"]
    return {
        "part_no": metadata.get("part_no") or metadata.get("source_id") or "",
        "name": metadata.get("name") or metadata.get("text_content") or "Unknown part",
        "score": hits[0]["score"],
    }


def _filters(filters: SearchFilters | None) -> dict[str, str] | None:
    return None if filters is None else filters.as_query()


def _merged_filters(filters: SearchFilters | None, extra: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    if filters is not None:
        merged.update(filters.as_query())
    merged.update(extra)
    return merged


def _metadata_seed(metadata: dict) -> str:
    parts = []
    for key in ("machine_type", "model_no", "fault_code", "part_no", "text_content", "source_id"):
        value = metadata.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if not text or text.lower() == "unknown":
            continue
        parts.append(text)
    return " ".join(parts)


def _identifier_filters(query: str, *, allowed: set[str] | None = None) -> dict[str, str]:
    identifiers = extract_identifiers(query)
    return {
        field: value
        for field, value in identifiers.items()
        if value and (allowed is None or field in allowed)
    }


def _manual_query(query: str) -> str:
    identifiers = extract_identifiers(query)
    parts = []
    if identifiers.get("fault_code"):
        parts.extend([identifiers["fault_code"], "fault response"])
    if identifiers.get("model_no"):
        parts.append(identifiers["model_no"])
    return " ".join(parts) if parts else query


def _rrf_merge(rankings: list[list[dict]]) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict] = {}
    for ranking in rankings:
        for index, item in enumerate(ranking, start=1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (60 + index)
            payloads[item_id] = item
    merged = [{"id": item_id, "score": score, "metadata": payloads[item_id]["metadata"]} for item_id, score in scores.items()]
    merged.sort(key=lambda item: item["score"], reverse=True)
    return merged[:10]
