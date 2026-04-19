from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DocType = Literal["manual", "incident", "part", "error_code", "voice_note"]
Severity = Literal["low", "medium", "high", "critical"]


class SearchFilters(BaseModel):
    doc_type: DocType | None = None
    machine_type: str | None = None
    model_no: str | None = None
    fault_code: str | None = None
    severity: Severity | None = None
    part_no: str | None = None

    def as_query(self) -> dict[str, str]:
        return self.model_dump(exclude_none=True)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    online: Literal[False]
    db: bool
    collection_ready: bool


class IngestRowRequest(BaseModel):
    row: dict[str, str | int | float | None]


class SearchTextRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: SearchFilters | None = None


class SearchResult(BaseModel):
    id: str
    score: float
    metadata: dict[str, str | int | float | None]


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str | None = None
    transcript: str | None = None


class ManualEvidence(BaseModel):
    source: str
    page: int | None
    snippet: str


class IncidentEvidence(BaseModel):
    id: str
    fix_applied: str
    downtime_min: int | None


class PartEvidence(BaseModel):
    part_no: str
    name: str


class DiagnoseEvidence(BaseModel):
    manual_section: ManualEvidence | None
    similar_incident: IncidentEvidence | None
    candidate_part: PartEvidence | None


class DiagnoseResponse(BaseModel):
    evidence: DiagnoseEvidence
    confidence: float
    recommended_steps: list[str]
    transcript: str | None = None
