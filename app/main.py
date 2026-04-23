# app/main.py

from fastapi import FastAPI
from datetime import datetime, timezone

from app.models import HealthResponse
from app.routes import router

app = FastAPI(
    title="DevOps Lab API",
    description="FastAPI service for CI/CD pipeline demonstration",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=app.version,
        timestamp=datetime.now(timezone.utc),
    )