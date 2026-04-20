from __future__ import annotations

import httpx

from app.config import settings
from app.pipelines.csv_loader import load_error_codes, load_incidents, load_parts


def main() -> None:
    base_url = f"http://localhost:{settings.backend_port}/api"
    raw_root = settings.raw_root
    with httpx.Client(base_url=base_url, timeout=60.0) as client:
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
            client.post(
                "/ingest/image",
                files={"file": (image_path.name, image_path.read_bytes(), "application/octet-stream")},
                data={"machine_type": "unknown"},
            ).raise_for_status()
            print(f"image {image_path.name}")

        for voice_path in sorted((raw_root / "voice").glob("*.wav")):
            client.post(
                "/ingest/voice",
                files={"file": (voice_path.name, voice_path.read_bytes(), "audio/wav")},
                data={"machine_type": "unknown"},
            ).raise_for_status()
            print(f"voice {voice_path.name}")

        incidents_path = raw_root / "incidents.csv"
        if incidents_path.exists():
            for row in load_incidents(str(incidents_path)):
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


if __name__ == "__main__":
    main()
