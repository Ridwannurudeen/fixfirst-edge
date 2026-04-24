"""End-to-end diagnose test driven by the fixture CSVs.

Exercises the full ingest->retrieve->diagnose path. Embeddings and the Actian
client are faked, but the service layer, metadata plumbing, filter routing,
recommended-step templating, and response schema all run for real.
"""
from __future__ import annotations

import asyncio
import csv
from pathlib import Path

import numpy as np
from httpx import ASGITransport, AsyncClient

from app.main import app

FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures"


def _load(name: str) -> list[dict[str, str]]:
    with (FIXTURES / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _manual_hit() -> dict:
    return {
        "id": "manual:conveyor_CX_200_service_manual.pdf:3:0",
        "score": 0.82,
        "metadata": {
            "doc_type": "manual",
            "machine_type": "Conveyor",
            "model_no": "CX-200",
            "source_id": "conveyor_CX_200_service_manual.pdf",
            "page": 3,
            "chunk_id": 0,
            "text_content": (
                "Error E04 indicates thermal overload on the drive motor. "
                "Reset the thermal overload relay and re-torque the motor mounts "
                "to 85 Nm before returning the unit to service."
            ),
        },
    }


def _incident_hit(inc: dict) -> dict:
    return {
        "id": f"incident:{inc['id']}",
        "score": 0.88,
        "metadata": {
            "doc_type": "incident",
            "machine_type": inc["machine_type"],
            "model_no": inc["model_no"],
            "fault_code": inc["fault_code"],
            "severity": inc["severity"],
            "source_id": inc["id"],
            "text_content": f"{inc['symptom']} {inc['fault_code']} {inc['fix_applied']}",
            "fix_applied": inc["fix_applied"],
            "downtime_min": int(inc["downtime_min"]) if inc.get("downtime_min") else None,
            "parts_used": inc.get("parts_used") or None,
            "verified": True,
        },
    }


def _part_hit(part: dict) -> dict:
    return {
        "id": f"part:{part['part_no']}",
        "score": 0.77,
        "metadata": {
            "doc_type": "part",
            "machine_type": part["machine_type"],
            "model_no": part["model_no"],
            "part_no": part["part_no"],
            "name": part["name"],
            "source_id": part["part_no"],
            "text_content": f"{part['part_no']} {part['name']}",
        },
    }


def test_diagnose_end_to_end_on_fixtures(monkeypatch) -> None:
    incidents = _load("incidents.csv")
    parts = _load("parts.csv")
    inc001 = next(i for i in incidents if i["id"] == "inc-001")
    ol_part = next(p for p in parts if p["part_no"] == "OL-E04-R")

    def fake_embed_text(_text: str) -> np.ndarray:
        return np.zeros(384, dtype=np.float32)

    def fake_search_hybrid(_query: str, _vec, filters, k: int = 10) -> list[dict]:
        doc_type = (filters or {}).get("doc_type")
        if doc_type == "manual":
            return [_manual_hit()]
        if doc_type == "incident":
            return [_incident_hit(inc001)]
        if doc_type == "part":
            return [_part_hit(ol_part)]
        return []

    monkeypatch.setattr("app.services.search_service.embed_text", fake_embed_text)
    monkeypatch.setattr("app.services.search_service.db.search_hybrid", fake_search_hybrid)

    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/diagnose",
                data={"query": "E04 motor overload on CX-200"},
            )
        assert response.status_code == 200
        body = response.json()

        manual = body["evidence"]["manual_section"]
        assert manual is not None
        assert manual["source"] == "conveyor_CX_200_service_manual.pdf"
        assert manual["page"] == 3
        assert "thermal overload" in manual["snippet"].lower()

        incident = body["evidence"]["similar_incident"]
        assert incident is not None
        assert incident["id"] == "inc-001"
        assert incident["fix_applied"].startswith("Replaced thermal overload relay")
        assert incident["downtime_min"] == 45

        part = body["evidence"]["candidate_part"]
        assert part is not None
        assert part["part_no"] == "OL-E04-R"
        assert part["name"] == "Thermal Overload Relay"

        steps = body["recommended_steps"]
        assert len(steps) == 3
        assert "conveyor_CX_200_service_manual.pdf p.3" in steps[0]
        assert "CX-200" in steps[1]
        assert "OL-E04-R" in steps[2]
        assert "Thermal Overload Relay" in steps[2]

        assert 0.0 < body["confidence"] <= 1.0

    asyncio.run(run())


def test_diagnose_honors_severity_filter(monkeypatch) -> None:
    incidents = _load("incidents.csv")
    parts = _load("parts.csv")
    critical_incident = next(i for i in incidents if i["severity"] == "critical")
    matching_part = next(
        (
            p
            for p in parts
            if p["machine_type"] == critical_incident["machine_type"]
            and p["model_no"] == critical_incident["model_no"]
        ),
        parts[0],
    )

    observed_filters: list[dict] = []

    def fake_embed_text(_text: str) -> np.ndarray:
        return np.zeros(384, dtype=np.float32)

    def fake_search_hybrid(_query: str, _vec, filters, k: int = 10) -> list[dict]:
        observed_filters.append(dict(filters or {}))
        doc_type = (filters or {}).get("doc_type")
        if doc_type == "manual":
            return [_manual_hit()]
        if doc_type == "incident":
            return [_incident_hit(critical_incident)]
        if doc_type == "part":
            return [_part_hit(matching_part)]
        return []

    monkeypatch.setattr("app.services.search_service.embed_text", fake_embed_text)
    monkeypatch.setattr("app.services.search_service.db.search_hybrid", fake_search_hybrid)

    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/diagnose",
                data={
                    "query": "seal leak",
                    "filters": '{"severity": "critical"}',
                },
            )
        assert response.status_code == 200
        body = response.json()
        assert body["evidence"]["similar_incident"]["id"] == critical_incident["id"]
        assert any(f.get("severity") == "critical" for f in observed_filters)
        part_filter = next(f for f in observed_filters if f.get("doc_type") == "part")
        assert part_filter.get("machine_type") == critical_incident["machine_type"]
        assert part_filter.get("model_no") == critical_incident["model_no"]

    asyncio.run(run())


def test_diagnose_requires_verified_incidents(monkeypatch) -> None:
    def fake_embed_text(_text: str) -> np.ndarray:
        return np.zeros(384, dtype=np.float32)

    def fake_search_hybrid(_query: str, _vec, filters, k: int = 10) -> list[dict]:
        doc_type = (filters or {}).get("doc_type")
        if doc_type == "manual":
            return [_manual_hit()]
        if doc_type == "incident":
            assert (filters or {}).get("verified") is True
            return [
                {
                    "id": "incident:inc-verified",
                    "score": 0.91,
                    "metadata": {
                        "doc_type": "incident",
                        "source_id": "inc-verified",
                        "model_no": "CX-200",
                        "machine_type": "Conveyor",
                        "fix_applied": "Replace relay and confirm current draw.",
                        "downtime_min": 18,
                        "verified": True,
                    },
                }
            ]
        if doc_type == "part":
            return [
                {
                    "id": "part:OL-E04-R",
                    "score": 0.77,
                    "metadata": {
                        "doc_type": "part",
                        "part_no": "OL-E04-R",
                        "name": "Thermal Overload Relay",
                        "source_id": "OL-E04-R",
                    },
                }
            ]
        return []

    monkeypatch.setattr("app.services.search_service.embed_text", fake_embed_text)
    monkeypatch.setattr("app.services.search_service.db.search_hybrid", fake_search_hybrid)

    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/diagnose", data={"query": "E04 motor overload on CX-200"})
        assert response.status_code == 200
        body = response.json()
        assert body["evidence"]["similar_incident"]["id"] == "inc-verified"

    asyncio.run(run())


def test_image_only_diagnose_uses_image_metadata_seed(monkeypatch) -> None:
    from app.services import search_service

    observed_queries: list[str] = []

    async def fake_search_image(_image, _filters):
        return [
            {
                "id": "image:schematic_01_conveyor_E04.png",
                "score": 1.0,
                "metadata": {
                    "doc_type": "incident",
                    "machine_type": "Conveyor",
                    "model_no": "CX-200",
                    "fault_code": "E04",
                    "part_no": "OL-E04-R",
                    "source_id": "schematic_01_conveyor_E04.png",
                    "text_content": "Conveyor CX-200 E04 OL-E04-R schematic",
                },
            }
        ]

    def fake_embed_text(text: str) -> np.ndarray:
        observed_queries.append(text)
        return np.zeros(384, dtype=np.float32)

    def fake_search_hybrid(query: str, _vec, filters, k: int = 10) -> list[dict]:
        observed_queries.append(query)
        doc_type = (filters or {}).get("doc_type")
        if doc_type == "manual":
            return [_manual_hit()]
        if doc_type == "incident":
            return [
                _incident_hit(
                    {
                        "id": "inc-001",
                        "machine_type": "Conveyor",
                        "model_no": "CX-200",
                        "fault_code": "E04",
                        "severity": "high",
                        "symptom": "Motor tripped on overload",
                        "fix_applied": "Replaced thermal overload relay and re-torqued motor mounts",
                        "downtime_min": "45",
                        "parts_used": "OL-E04-R",
                    }
                )
            ]
        if doc_type == "part":
            return [
                _part_hit(
                    {
                        "part_no": "OL-E04-R",
                        "name": "Thermal Overload Relay",
                        "machine_type": "Conveyor",
                        "model_no": "CX-200",
                    }
                )
            ]
        return []

    monkeypatch.setattr(search_service, "search_image", fake_search_image)
    monkeypatch.setattr(search_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(search_service.db, "search_hybrid", fake_search_hybrid)

    async def run() -> None:
        result = await search_service.diagnose(None, object(), None, None)
        assert result.evidence.similar_incident is not None
        assert result.evidence.similar_incident.id == "inc-001"
        assert result.evidence.candidate_part is not None
        assert result.evidence.candidate_part.part_no == "OL-E04-R"

    asyncio.run(run())
    assert any("CX-200" in query and "E04" in query and "OL-E04-R" in query for query in observed_queries)
