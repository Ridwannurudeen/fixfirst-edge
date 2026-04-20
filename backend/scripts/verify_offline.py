from __future__ import annotations

import os
from pathlib import Path

import httpx

from app.config import settings


def _status_line(name: str, status: str, detail: str) -> None:
    print(f"[{name:<9}] {status:<4} {detail}")


def _pick_first(path: Path, patterns: tuple[str, ...]) -> Path | None:
    for pattern in patterns:
        for candidate in sorted(path.glob(pattern)):
            if candidate.is_file():
                return candidate
    return None


def main() -> None:
    backend_url = os.getenv("FIXFIRST_BACKEND_URL", f"http://localhost:{settings.backend_port}")
    proxy_vars = [name for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy") if os.getenv(name)]
    proxy_detail = ", ".join(proxy_vars) if proxy_vars else "none set"
    if proxy_vars:
        print(f"[preflight] WARNING proxies set: {proxy_detail}")
    else:
        print(f"[preflight] proxies: {proxy_detail}")
    print(f"[preflight] backend: {backend_url}")

    checks_run = 0
    passed = 0
    failed = 0

    def record(name: str, ok: bool, detail: str) -> None:
        nonlocal checks_run, passed, failed
        checks_run += 1
        if ok:
            passed += 1
            _status_line(name, "PASS", detail)
        else:
            failed += 1
            _status_line(name, "FAIL", detail)

    with httpx.Client(base_url=backend_url, timeout=20.0) as client:
        try:
            health = client.get("/api/health")
            health.raise_for_status()
            payload = health.json()
            ok = (
                payload.get("status") == "ok"
                and payload.get("db") is True
                and payload.get("collection_ready") is True
            )
            detail = (
                f"db={payload.get('db')} collection_ready={payload.get('collection_ready')}"
                if ok
                else "run bulk_ingest after the backend and database are up"
            )
            record("health", ok, detail)
        except Exception as exc:
            record("health", False, str(exc))

        try:
            response = client.post("/api/diagnose", data={"query": "E04 motor overload on CX-200"})
            response.raise_for_status()
            body = response.json()
            evidence = body.get("evidence", {})
            slots = (
                evidence.get("manual_section"),
                evidence.get("similar_incident"),
                evidence.get("candidate_part"),
            )
            ok = all(slot is not None for slot in slots) and len(body.get("recommended_steps", [])) >= 1
            record("text", ok, f"{sum(slot is not None for slot in slots)}/3 evidence slots")
        except Exception as exc:
            record("text", False, str(exc))

        images_dir = settings.raw_root / "images"
        image_path = _pick_first(images_dir, ("*.png", "*.jpg", "*.jpeg"))
        if image_path is None:
            _status_line("image", "SKIP", f"no image fixtures under {images_dir}")
        else:
            try:
                with image_path.open("rb") as handle:
                    response = client.post(
                        "/api/diagnose",
                        files={"image": (image_path.name, handle.read(), "application/octet-stream")},
                    )
                response.raise_for_status()
                body = response.json()
                evidence = body.get("evidence", {})
                ok = any(value is not None for value in evidence.values())
                record("image", ok, image_path.name)
            except Exception as exc:
                record("image", False, str(exc))

        voice_dir = settings.raw_root / "voice"
        voice_path = _pick_first(voice_dir, ("*.wav",))
        if voice_path is None:
            _status_line("voice", "SKIP", f"no voice fixtures under {voice_dir}")
        else:
            try:
                with voice_path.open("rb") as handle:
                    response = client.post(
                        "/api/diagnose",
                        files={"voice": (voice_path.name, handle.read(), "audio/wav")},
                    )
                response.raise_for_status()
                body = response.json()
                transcript = body.get("transcript")
                ok = isinstance(transcript, str) and transcript.strip() != ""
                detail = f'transcript: "{transcript[:48]}..."' if ok else "empty transcript"
                record("voice", ok, detail)
            except Exception as exc:
                record("voice", False, str(exc))

    summary = "PASS" if failed == 0 else "FAIL"
    print()
    print(f"verify_offline: {summary} ({passed}/{checks_run})")
    raise SystemExit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
