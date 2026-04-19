from fastapi import FastAPI

from app.routers.diagnose import router as diagnose_router
from app.routers.health import router as health_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router

app = FastAPI(title="FixFirst Edge")
app.include_router(health_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(diagnose_router, prefix="/api")
