from __future__ import annotations

import re
from collections.abc import Iterable

_FAULT_CODE_RE = re.compile(r"\b[A-Z]{1,4}\d{2,4}[A-Z]?\b")
_MODEL_NO_RE = re.compile(r"\b[A-Z]{1,6}-\d{1,6}[A-Z0-9]*\b")
_PART_NO_RE = re.compile(r"\b[A-Z0-9]{1,6}(?:-[A-Z0-9]{1,8}){2,}\b")


def extract_identifiers(text: str) -> dict[str, str]:
    normalized = text.upper()
    part_candidates = _unique(_PART_NO_RE.findall(normalized))
    model_candidates = _unique(
        candidate for candidate in _MODEL_NO_RE.findall(normalized) if candidate not in part_candidates
    )
    fault_candidates = _unique(
        candidate
        for candidate in _FAULT_CODE_RE.findall(normalized)
        if candidate not in part_candidates and candidate not in model_candidates
    )
    return {
        "fault_code": fault_candidates[0] if fault_candidates else "",
        "model_no": model_candidates[0] if model_candidates else "",
        "part_no": part_candidates[0] if part_candidates else "",
    }


def fill_identifier_fields(metadata: dict[str, str | int | None], text: str) -> None:
    identifiers = extract_identifiers(text)
    for field_name, value in identifiers.items():
        if value and not metadata.get(field_name):
            metadata[field_name] = value


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
