from fastapi import FastAPI
from datetime import datetime, timezone

from app.models import HealthResponse
from app.routes import router
from app.metrics import PrometheusMiddleware, metrics_response

app = FastAPI(
    title="DevOps Lab API",
    description="FastAPI service for CI/CD pipeline demonstration",
    version="1.0.0",
)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=app.version,
        timestamp=datetime.now(timezone.utc),
    )


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Prometheus metrics endpoint."""
    return metrics_response()