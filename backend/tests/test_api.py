from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def test_health_endpoint(monkeypatch) -> None:
    from app import db
    from app.routers.health import health

    monkeypatch.setattr(db, "health", lambda: True)
    monkeypatch.setattr(db, "collection_ready", lambda: True)

    response = health()

    assert response.status == "ok"
    assert response.db is True
    assert response.collection_ready is True


def test_search_text_endpoint(monkeypatch) -> None:
    from app.routers.search import search_text
    from app.schemas import SearchTextRequest
    from app.services import search_service

    def fake_search_text(query: str, filters):
        return [{"id": "manual:1", "score": 0.9, "metadata": {"text_content": query}}]

    monkeypatch.setattr(search_service, "search_text", fake_search_text)

    response = search_text(SearchTextRequest(query="E04 overload"))

    assert response.results[0].id == "manual:1"


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
