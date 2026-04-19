from __future__ import annotations

import json

import httpx


def main() -> None:
    with httpx.Client(base_url="http://localhost:8000", timeout=20.0) as client:
        health = client.get("/api/health")
        health.raise_for_status()
        print("health")
        print(json.dumps(health.json(), indent=2))

        diagnose = client.post("/api/search/text", json={"query": "E04 motor overload"})
        diagnose.raise_for_status()
        print("search-text")
        print(json.dumps(diagnose.json(), indent=2))


if __name__ == "__main__":
    main()
