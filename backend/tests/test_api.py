from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def test_health_endpoint() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    asyncio.run(run())


def test_search_text_endpoint(monkeypatch) -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)

        def fake_search_text(query: str, filters):
            return [{"id": "manual:1", "score": 0.9, "metadata": {"text_content": query}}]

        from app.services import search_service

        monkeypatch.setattr(search_service, "search_text", fake_search_text)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/search/text", json={"query": "E04 overload"})
        assert response.status_code == 200
        assert response.json()["results"][0]["id"] == "manual:1"

    asyncio.run(run())


def test_cors_preflight_allows_local_frontend() -> None:
    async def run() -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.options(
                "/api/diagnose",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                },
            )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    asyncio.run(run())
