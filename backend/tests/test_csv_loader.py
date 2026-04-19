from __future__ import annotations

import csv

import pytest

from app.pipelines.csv_loader import load_error_codes, load_incidents, load_parts


def test_load_incidents_reads_rows(tmp_path):
    path = tmp_path / "incidents.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "machine_type",
                "model_no",
                "fault_code",
                "severity",
                "symptom",
                "fix_applied",
                "downtime_min",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "inc-1",
                "machine_type": "pump",
                "model_no": "p-10",
                "fault_code": "E04",
                "severity": "high",
                "symptom": "stalled",
                "fix_applied": "replace belt",
                "downtime_min": "15",
            }
        )
    rows = load_incidents(str(path))
    assert rows[0]["fault_code"] == "E04"


def test_load_parts_requires_columns(tmp_path):
    path = tmp_path / "parts.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["part_no", "name"])
        writer.writeheader()
        writer.writerow({"part_no": "P-1", "name": "Bearing"})
    with pytest.raises(ValueError):
        load_parts(str(path))


def test_load_error_codes_reads_rows(tmp_path):
    path = tmp_path / "codes.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fault_code", "machine_type", "description"])
        writer.writeheader()
        writer.writerow({"fault_code": "E04", "machine_type": "pump", "description": "Overload"})
    rows = load_error_codes(str(path))
    assert rows[0]["description"] == "Overload"
