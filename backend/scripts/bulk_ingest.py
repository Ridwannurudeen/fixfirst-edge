from __future__ import annotations

import re

import httpx

from app.config import settings
from app.pipelines.identifier_extractor import extract_identifiers
from app.pipelines.csv_loader import load_error_codes, load_incidents, load_parts


def main() -> None:
    base_url = f"http://localhost:{settings.backend_port}/api"
    raw_root = settings.raw_root
    incidents_path = raw_root / "incidents.csv"
    incident_rows = load_incidents(str(incidents_path)) if incidents_path.exists() else []

    with httpx.Client(base_url=base_url, timeout=180.0) as client:
        for pdf_path in sorted((raw_root / "manuals").glob("*.pdf")):
            client.post(
                "/ingest/manual",
                files={"file": (pdf_path.name, pdf_path.read_bytes(), "application/pdf")},
                data={"machine_type": "unknown", "model_no": pdf_path.stem},
            ).raise_for_status()
            print(f"manual {pdf_path.name}")

        for image_path in sorted((raw_root / "images").glob("*")):
            if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            image_metadata = _image_metadata(image_path.name, incident_rows)
            client.post(
                "/ingest/image",
                files={"file": (image_path.name, image_path.read_bytes(), "application/octet-stream")},
                data=image_metadata,
            ).raise_for_status()
            print(f"image {image_path.name}")

        for voice_path in sorted((raw_root / "voice").glob("*.wav")):
            client.post(
                "/ingest/voice",
                files={"file": (voice_path.name, voice_path.read_bytes(), "audio/wav")},
                data={"machine_type": "unknown"},
            ).raise_for_status()
            print(f"voice {voice_path.name}")

        if incidents_path.exists():
            for row in incident_rows:
                client.post("/ingest/incident", json={"row": {**row, "verified": True}}).raise_for_status()
            print(f"incidents {incidents_path.name}")

        parts_path = raw_root / "parts.csv"
        if parts_path.exists():
            for row in load_parts(str(parts_path)):
                client.post("/ingest/part", json={"row": row}).raise_for_status()
            print(f"parts {parts_path.name}")

        error_codes_path = raw_root / "error_codes.csv"
        if error_codes_path.exists():
            for row in load_error_codes(str(error_codes_path)):
                client.post("/ingest/incident", json={"row": {**row, "verified": True}}).raise_for_status()
            print(f"error-codes {error_codes_path.name}")


def _image_metadata(filename: str, incidents: list[dict[str, str]]) -> dict[str, str]:
    stem = filename.rsplit(".", 1)[0]
    normalized = stem.replace("_", " ").replace("-", " ")
    identifiers = extract_identifiers(normalized)
    fault_code = identifiers.get("fault_code", "")
    machine_type = _machine_type_from_name(normalized, incidents) or "unknown"
    matching_incident = _matching_incident(filename, machine_type, fault_code, incidents)

    payload: dict[str, str] = {
        "machine_type": matching_incident.get("machine_type") if matching_incident else machine_type,
    }
    for field in ("model_no", "fault_code", "severity"):
        value = matching_incident.get(field) if matching_incident else ""
        if field == "fault_code" and not value:
            value = fault_code
        if value:
            payload[field] = value
    part_no = matching_incident.get("parts_used", "") if matching_incident else ""
    if part_no:
        payload["part_no"] = part_no.split(",", 1)[0].strip()
    return payload


def _machine_type_from_name(text: str, incidents: list[dict[str, str]]) -> str | None:
    lower_text = text.lower()
    machine_types = sorted({row.get("machine_type", "") for row in incidents if row.get("machine_type")})
    for machine_type in machine_types:
        if machine_type.lower() in lower_text:
            return machine_type
    return None


def _matching_incident(
    filename: str,
    machine_type: str,
    fault_code: str,
    incidents: list[dict[str, str]],
) -> dict[str, str] | None:
    generated_map = {
        "01": "inc-001",
        "02": "inc-003",
        "03": "inc-008",
        "04": "inc-007",
        "05": "inc-013",
        "06": "inc-025",
    }
    index_match = re.search(r"schematic_(\d{2})_", filename)
    if index_match:
        wanted_id = generated_map.get(index_match.group(1))
        if wanted_id:
            for row in incidents:
                if row.get("id") == wanted_id:
                    return row

    for row in incidents:
        if machine_type != "unknown" and row.get("machine_type") != machine_type:
            continue
        if fault_code and row.get("fault_code") != fault_code:
            continue
        return row
    return None


if __name__ == "__main__":
    main()
