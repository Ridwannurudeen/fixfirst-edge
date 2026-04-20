from __future__ import annotations

from app.pipelines.identifier_extractor import extract_identifiers, fill_identifier_fields


def test_extract_identifiers_from_maintenance_query() -> None:
    identifiers = extract_identifiers("E04 motor overload on CX-200. likely OL-E04-R relay")

    assert identifiers == {
        "fault_code": "E04",
        "model_no": "CX-200",
        "part_no": "OL-E04-R",
    }


def test_fill_identifier_fields_only_backfills_missing_values() -> None:
    metadata: dict[str, str | int | None] = {
        "fault_code": None,
        "model_no": "CX-200",
        "part_no": None,
    }

    fill_identifier_fields(metadata, "Thermal overload on E04 requires relay OL-E04-R")

    assert metadata["fault_code"] == "E04"
    assert metadata["model_no"] == "CX-200"
    assert metadata["part_no"] == "OL-E04-R"
