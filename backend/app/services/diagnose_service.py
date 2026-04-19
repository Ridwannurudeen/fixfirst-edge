from __future__ import annotations


def build_recommended_steps(
    manual_section: dict | None,
    similar_incident: dict | None,
    candidate_part: dict | None,
) -> tuple[list[str], float]:
    steps: list[str] = []
    scores: list[float] = []

    if manual_section is not None:
        steps.append(
            f"Per {manual_section['source']} p.{manual_section['page']}: {manual_section['snippet'][:200]}"
        )
        scores.append(float(manual_section.get("score", 0.0)))

    if similar_incident is not None:
        steps.append(
            "Previous incident on "
            f"{similar_incident['machine_id']} resolved by: {similar_incident['fix_applied']} "
            f"(downtime: {similar_incident['downtime_min']} min)"
        )
        scores.append(float(similar_incident.get("score", 0.0)))

    if candidate_part is not None:
        steps.append(f"Likely replacement part: {candidate_part['part_no']} ({candidate_part['name']})")
        scores.append(float(candidate_part.get("score", 0.0)))

    confidence = float(sum(scores) / len(scores)) if scores else 0.0
    return steps, confidence
