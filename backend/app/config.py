from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[2]
    data_root: Path = project_root / "data"
    raw_root: Path = data_root / "raw"
    processed_root: Path = data_root / "processed"
    model_cache_dir: Path = Path(os.getenv("MODEL_CACHE_DIR", "./data/processed/models"))
    actian_host: str = os.getenv("ACTIAN_HOST", "localhost")
    actian_port: int = int(os.getenv("ACTIAN_PORT", "50051"))
    actian_api_key: str = os.getenv("ACTIAN_API_KEY", "")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    collection_name: str = "incidents"

    @property
    def actian_url(self) -> str:
        return f"{self.actian_host}:{self.actian_port}"


settings = Settings()
