from __future__ import annotations

import numpy as np

from app import db


def test_search_hybrid_uses_identifier_filtered_actian_branches(monkeypatch) -> None:
    calls: list[dict | None] = []

    def fake_search_vector(_vector_name: str, _query_vec, filters, k: int) -> list[dict]:
        calls.append(None if filters is None else dict(filters))
        merged_filters = filters or {}
        if merged_filters.get("fault_code") == "E04" and merged_filters.get("model_no") == "CX-200":
            return [
                {
                    "id": "manual:e04-cx200",
                    "score": 0.91,
                    "metadata": {
                        "doc_id": "manual:e04-cx200",
                        "fault_code": "E04",
                        "model_no": "CX-200",
                    },
                }
            ]
        if merged_filters.get("fault_code") == "E04":
            return [
                {
                    "id": "manual:e04",
                    "score": 0.87,
                    "metadata": {
                        "doc_id": "manual:e04",
                        "fault_code": "E04",
                    },
                }
            ]
        return [
            {
                "id": "manual:dense",
                "score": 0.75,
                "metadata": {"doc_id": "manual:dense"},
            }
        ]

    monkeypatch.setattr(db, "init_collection", lambda: None)
    monkeypatch.setattr(db, "_search_vector", fake_search_vector)

    results = db.search_hybrid(
        "E04 motor overload on CX-200",
        np.zeros(384, dtype=np.float32),
        {"doc_type": "manual"},
        k=5,
    )

    assert results[0]["id"] == "manual:e04-cx200"
    assert calls[0] == {"doc_type": "manual"}
    assert {"doc_type": "manual", "fault_code": "E04", "model_no": "CX-200"} in calls
    assert {"doc_type": "manual", "fault_code": "E04"} in calls


def test_init_collection_ensures_indexes_for_existing_collection(monkeypatch) -> None:
    ensured: list[object] = []

    class FakeCollections:
        def exists(self, _name: str) -> bool:
            return True

        def create(self, *_args, **_kwargs) -> None:  # pragma: no cover - should not be called
            raise AssertionError("collection should not be recreated")

    class FakeClient:
        collections = FakeCollections()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_client = FakeClient()

    monkeypatch.setattr(db, "_require_client", lambda: None)
    monkeypatch.setattr(db, "_client", lambda: fake_client)
    monkeypatch.setattr(db, "_ensure_field_indexes", lambda client: ensured.append(client))
    monkeypatch.setattr(db, "_COLLECTION_READY", False)

    db.init_collection()

    assert ensured == [fake_client]
    assert db._COLLECTION_READY is True
