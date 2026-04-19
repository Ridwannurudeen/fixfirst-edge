from __future__ import annotations

import json

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas import DiagnoseResponse, SearchFilters
from app.services import search_service

router = APIRouter(tags=["diagnose"])


def _parse_filters(raw_filters: str | None) -> SearchFilters | None:
    if raw_filters is None or raw_filters.strip() == "":
        return None
    return SearchFilters.model_validate(json.loads(raw_filters))


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(
    query: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    voice: UploadFile | None = File(default=None),
    filters: str | None = Form(default=None),
) -> DiagnoseResponse:
    parsed_filters = _parse_filters(filters)
    return await search_service.diagnose(query, image, voice, parsed_filters)
