from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas import IncidentRowRequest, PartRowRequest
from app.services import ingest_service

router = APIRouter(tags=["ingest"])


@router.post("/ingest/manual")
async def ingest_manual(
    file: UploadFile = File(...),
    machine_type: str = Form(...),
    model_no: str = Form(...),
) -> dict[str, int]:
    count = await ingest_service.ingest_manual(file, machine_type, model_no)
    return {"count": count}


@router.post("/ingest/incident")
async def ingest_incident(body: IncidentRowRequest) -> dict[str, str]:
    doc_id = ingest_service.ingest_incident(body.row.model_dump())
    return {"id": doc_id}


@router.post("/ingest/image")
async def ingest_image(
    file: UploadFile = File(...),
    machine_type: str = Form(...),
    model_no: str | None = Form(default=None),
    fault_code: str | None = Form(default=None),
    severity: str | None = Form(default=None),
    part_no: str | None = Form(default=None),
) -> dict[str, str]:
    doc_id = await ingest_service.ingest_image(file, machine_type, model_no, fault_code, severity, part_no)
    return {"id": doc_id}


@router.post("/ingest/voice")
async def ingest_voice(
    file: UploadFile = File(...),
    machine_type: str = Form(...),
) -> dict[str, str]:
    doc_id = await ingest_service.ingest_voice(file, machine_type)
    return {"id": doc_id}


@router.post("/ingest/part")
async def ingest_part(body: PartRowRequest) -> dict[str, str]:
    doc_id = ingest_service.ingest_part(body.row.model_dump())
    return {"id": doc_id}


@router.post("/incident/save")
async def save_incident(body: IncidentRowRequest) -> dict[str, str]:
    doc_id = ingest_service.ingest_incident(body.row.model_dump())
    return {"id": doc_id}
