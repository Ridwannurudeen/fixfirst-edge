from __future__ import annotations

from app.services.diagnose_service import build_recommended_steps


def test_build_recommended_steps_and_confidence():
    steps, confidence = build_recommended_steps(
        {"source": "manual.pdf", "page": 3, "snippet": "Check the overload relay.", "score": 0.8},
        {"machine_id": "line-3", "fix_applied": "Reset relay", "downtime_min": 12, "score": 0.7},
        {"part_no": "P-100", "name": "Overload Relay", "score": 0.6},
    )
    assert len(steps) == 3
    assert steps[0].startswith("Per manual.pdf p.3:")
    assert round(confidence, 2) == 0.7
