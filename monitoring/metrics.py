"""Production monitoring metrics for ForesightAI.

Collects and exposes Prometheus-compatible metrics for:
  - FastAPI request latency and error rates
  - ML inference latency and prediction distribution
  - Database connection pool stats
  - System resource usage (CPU, RAM)
  - Business KPIs (predictions per minute, confidence distribution)

Usage with FastAPI::

    from monitoring.metrics import setup_metrics, get_metrics_registry
    from fastapi import FastAPI
    from prometheus_client import make_asgi_app

    app = FastAPI()
    setup_metrics(app)
    app.mount("/metrics", make_asgi_app())
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Generator, Optional

import psutil

try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Summary,
        CollectorRegistry,
        REGISTRY,
    )
    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False
    logging.getLogger(__name__).warning(
        "prometheus_client not installed. Metrics will be no-ops."
    )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Registry (use default unless testing)
# ---------------------------------------------------------------------------
_registry: Optional[object] = None


def get_registry():
    """Return the active Prometheus CollectorRegistry."""
    return _registry or (REGISTRY if _PROMETHEUS_AVAILABLE else None)


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

def _make_metrics():
    """Instantiate all metric objects. Called once at startup."""
    if not _PROMETHEUS_AVAILABLE:
        return {}

    reg = get_registry()
    kwargs = {} if reg is REGISTRY else {"registry": reg}

    metrics = {
        # HTTP layer
        "http_requests_total": Counter(
            "foresightai_http_requests_total",
            "Total HTTP requests received.",
            ["method", "endpoint", "status_code"],
            **kwargs,
        ),
        "http_request_duration_seconds": Histogram(
            "foresightai_http_request_duration_seconds",
            "HTTP request latency in seconds.",
            ["method", "endpoint"],
            buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            **kwargs,
        ),
        "http_errors_total": Counter(
            "foresightai_http_errors_total",
            "Total HTTP 4xx/5xx responses.",
            ["method", "endpoint", "error_type"],
            **kwargs,
        ),
        # ML inference
        "prediction_requests_total": Counter(
            "foresightai_prediction_requests_total",
            "Total ML prediction requests.",
            ["outcome"],
            **kwargs,
        ),
        "prediction_latency_seconds": Histogram(
            "foresightai_prediction_latency_seconds",
            "ML inference latency (preprocessor + model forward pass).",
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            **kwargs,
        ),
        "prediction_confidence_score": Histogram(
            "foresightai_prediction_confidence_score",
            "Distribution of model confidence scores.",
            buckets=[0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 1.0],
            **kwargs,
        ),
        "shap_latency_seconds": Histogram(
            "foresightai_shap_latency_seconds",
            "SHAP explanation computation latency.",
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
            **kwargs,
        ),
        # Simulation
        "simulation_requests_total": Counter(
            "foresightai_simulation_requests_total",
            "Total Monte Carlo simulation requests.",
            ["scenario"],
            **kwargs,
        ),
        "simulation_latency_seconds": Histogram(
            "foresightai_simulation_latency_seconds",
            "Monte Carlo simulation latency.",
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            **kwargs,
        ),
        # Database
        "db_query_duration_seconds": Histogram(
            "foresightai_db_query_duration_seconds",
            "Database query latency.",
            ["operation"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            **kwargs,
        ),
        "db_active_connections": Gauge(
            "foresightai_db_active_connections",
            "Number of active database connections.",
            **kwargs,
        ),
        # System resources
        "system_cpu_usage_percent": Gauge(
            "foresightai_system_cpu_usage_percent",
            "System CPU usage percentage.",
            **kwargs,
        ),
        "system_memory_usage_bytes": Gauge(
            "foresightai_system_memory_usage_bytes",
            "System memory usage in bytes.",
            **kwargs,
        ),
        "system_memory_available_bytes": Gauge(
            "foresightai_system_memory_available_bytes",
            "Available system memory in bytes.",
            **kwargs,
        ),
        # Business KPIs
        "predictions_per_minute": Gauge(
            "foresightai_predictions_per_minute",
            "Rolling predictions per minute (1-min window).",
            **kwargs,
        ),
        "model_version_info": Gauge(
            "foresightai_model_version_info",
            "Currently loaded ML model version.",
            ["version"],
            **kwargs,
        ),
    }
    logger.info("Prometheus metrics initialised: %d metrics registered.", len(metrics))
    return metrics


_METRICS: dict = {}


def setup_metrics(app=None, model_version: str = "1.0.0") -> None:
    """Initialise all Prometheus metrics and wire up FastAPI middleware.

    Call once at application startup.

    Args:
        app: FastAPI application instance (optional; used for middleware).
        model_version: Current ML model version string for labelling.
    """
    global _METRICS
    _METRICS = _make_metrics()

    # Set static model version gauge
    if "model_version_info" in _METRICS:
        _METRICS["model_version_info"].labels(version=model_version).set(1)

    if app is not None:
        app.add_middleware(_MetricsMiddleware)
        logger.info("Prometheus middleware attached to FastAPI app.")

    # Start background system metrics collector
    _update_system_metrics()
    logger.info("Metrics setup complete (model_version=%s).", model_version)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

class _MetricsMiddleware:
    """ASGI middleware that records HTTP request metrics."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path   = scope.get("path", "/")
        t0     = time.perf_counter()
        status = [200]

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status[0] = message.get("status", 200)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            elapsed = time.perf_counter() - t0
            sc = str(status[0])

            if _PROMETHEUS_AVAILABLE and _METRICS:
                _METRICS["http_requests_total"].labels(
                    method=method, endpoint=path, status_code=sc
                ).inc()
                _METRICS["http_request_duration_seconds"].labels(
                    method=method, endpoint=path
                ).observe(elapsed)
                if status[0] >= 400:
                    _METRICS["http_errors_total"].labels(
                        method=method, endpoint=path,
                        error_type="4xx" if status[0] < 500 else "5xx"
                    ).inc()


# ---------------------------------------------------------------------------
# Context managers for ML / DB timing
# ---------------------------------------------------------------------------

@contextmanager
def track_prediction(outcome: str = "unknown") -> Generator:
    """Context manager that records ML prediction latency and count.

    Args:
        outcome: Predicted class label (e.g. 'Approved', 'Rejected').

    Yields:
        None
    """
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t0
        if _PROMETHEUS_AVAILABLE and _METRICS:
            _METRICS["prediction_requests_total"].labels(outcome=outcome).inc()
            _METRICS["prediction_latency_seconds"].observe(elapsed)


@contextmanager
def track_shap() -> Generator:
    """Context manager that records SHAP explanation latency."""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        if _PROMETHEUS_AVAILABLE and _METRICS:
            _METRICS["shap_latency_seconds"].observe(time.perf_counter() - t0)


@contextmanager
def track_simulation(scenario: str = "custom") -> Generator:
    """Context manager that records simulation latency and count.

    Args:
        scenario: Name of the scenario being simulated.
    """
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t0
        if _PROMETHEUS_AVAILABLE and _METRICS:
            _METRICS["simulation_requests_total"].labels(scenario=scenario).inc()
            _METRICS["simulation_latency_seconds"].observe(elapsed)


@contextmanager
def track_db_query(operation: str = "query") -> Generator:
    """Context manager that records database query latency.

    Args:
        operation: Type of database operation ('select', 'insert', etc.).
    """
    t0 = time.perf_counter()
    try:
        yield
    finally:
        if _PROMETHEUS_AVAILABLE and _METRICS:
            _METRICS["db_query_duration_seconds"].labels(operation=operation).observe(
                time.perf_counter() - t0
            )


def record_confidence(score: float) -> None:
    """Record a model confidence score observation.

    Args:
        score: Confidence score in [0, 1].
    """
    if _PROMETHEUS_AVAILABLE and _METRICS:
        _METRICS["prediction_confidence_score"].observe(score)


def _update_system_metrics() -> None:
    """Refresh CPU and memory Gauges from psutil."""
    if not (_PROMETHEUS_AVAILABLE and _METRICS):
        return
    try:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        _METRICS["system_cpu_usage_percent"].set(cpu)
        _METRICS["system_memory_usage_bytes"].set(mem.used)
        _METRICS["system_memory_available_bytes"].set(mem.available)
    except Exception as exc:
        logger.warning("Could not update system metrics: %s", exc)
