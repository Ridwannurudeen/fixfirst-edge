from __future__ import annotations

from pathlib import Path

import pandas as pd


def _load_csv(path: str, required_columns: set[str]) -> list[dict]:
    frame = pd.read_csv(Path(path))
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing required columns: {joined}")
    return frame.to_dict(orient="records")


def load_incidents(path: str) -> list[dict]:
    return _load_csv(
        path,
        {
            "id",
            "machine_type",
            "model_no",
            "fault_code",
            "severity",
            "symptom",
            "fix_applied",
            "downtime_min",
        },
    )


def load_parts(path: str) -> list[dict]:
    return _load_csv(path, {"part_no", "name", "machine_type", "model_no"})


def load_error_codes(path: str) -> list[dict]:
    return _load_csv(path, {"fault_code", "machine_type", "description"})
