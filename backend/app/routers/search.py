from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas import SearchFilters, SearchResponse, SearchTextRequest
from app.services import search_service

router = APIRouter(tags=["search"])


def _parse_filters(raw_filters: str | None) -> SearchFilters | None:
    if raw_filters is None or raw_filters.strip() == "":
        return None
    parsed = json.loads(raw_filters)
    return SearchFilters.model_validate(parsed)


@router.post("/search/text", response_model=SearchResponse)
def search_text(body: SearchTextRequest) -> SearchResponse:
    results = search_service.search_text(body.query, body.filters)
    return SearchResponse(results=results, query=body.query)


@router.post("/search/image", response_model=SearchResponse)
async def search_image(
    file: UploadFile = File(...),
    filters: str | None = Form(default=None),
) -> SearchResponse:
    parsed_filters = _parse_filters(filters)
    results = await search_service.search_image(file, parsed_filters)
    return SearchResponse(results=results)


@router.post("/search/voice", response_model=SearchResponse)
async def search_voice(
    file: UploadFile = File(...),
    filters: str | None = Form(default=None),
) -> SearchResponse:
    parsed_filters = _parse_filters(filters)
    transcript, results = await search_service.search_voice(file, parsed_filters)
    return SearchResponse(results=results, transcript=transcript)


@router.post("/search/multimodal", response_model=SearchResponse)
async def search_multimodal(
    text: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    audio: UploadFile | None = File(default=None),
    filters: str | None = Form(default=None),
) -> SearchResponse:
    parsed_filters = _parse_filters(filters)
    transcript, results = await search_service.search_multimodal(text, image, audio, parsed_filters)
    return SearchResponse(results=results, query=text, transcript=transcript)
