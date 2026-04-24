import time
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY,
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ─── Metric Definitions ────────────────────────────────────────
# These are the SLIs (Service Level Indicators) we'll build SLOs on

# Counter: Total requests by method, endpoint, and status code
# This gives us the error rate SLI: rate of 5xx / rate of total
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

# Histogram: Request duration in seconds
# This gives us the latency SLI: % of requests under threshold
# Buckets chosen to capture the interesting range for a web API
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Gauge: Currently in-flight requests
# Useful for capacity planning, not directly an SLO metric
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method"],
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware that records RED metrics for every request."""

    async def dispatch(self, request: Request, call_next):
        # Don't instrument the metrics endpoint itself (avoid recursion)
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        # Normalize path to avoid cardinality explosion
        # /api/items/abc123 → /api/items/{id}
        path = self._normalize_path(request.url.path)

        REQUESTS_IN_PROGRESS.labels(method=method).inc()
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=str(status_code),
            ).inc()
            REQUEST_DURATION.labels(
                method=method,
                endpoint=path,
            ).observe(duration)
            REQUESTS_IN_PROGRESS.labels(method=method).dec()

        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Replace dynamic path segments with placeholders.

        This prevents high-cardinality labels which kill Prometheus performance.
        /api/items/abc-123 → /api/items/{id}
        """
        parts = path.strip("/").split("/")
        normalized = []
        for i, part in enumerate(parts):
            # If the previous part is "items" and this looks like an ID, replace it
            if i > 0 and parts[i - 1] == "items" and len(part) > 8:
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/" + "/".join(normalized) if normalized else "/"


def metrics_response() -> Response:
    """Generate the /metrics endpoint response in Prometheus format."""
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )