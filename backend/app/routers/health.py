from fastapi import APIRouter

from app import db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_up = db.health()
    return HealthResponse(
        status="ok",
        online=False,
        db=db_up,
        collection_ready=db_up and db.collection_ready(),
    )
