"""Health check endpoints and readiness probes for ForesightAI.

Provides structured health checks for all system dependencies:
  - Database connectivity
  - ML model readiness
  - MLflow registry availability
  - System resource thresholds
  - API endpoint liveness

Compatible with Kubernetes liveness / readiness probes and
load-balancer health checks.
"""

import logging
import os
import time
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"


class CheckResult:
    """Result of a single health check component.

    Attributes:
        name: Component name.
        status: HealthStatus value.
        details: Optional diagnostic details.
        latency_ms: Time taken to perform the check in milliseconds.
    """

    def __init__(
        self,
        name: str,
        status: HealthStatus,
        details: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
    ) -> None:
        self.name = name
        self.status = status
        self.details = details or {}
        self.latency_ms = round(latency_ms, 2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to JSON-safe dict."""
        return {
            "name": self.name,
            "status": self.status.value,
            "details": self.details,
            "latency_ms": self.latency_ms,
        }

    @property
    def is_healthy(self) -> bool:
        """True if status is HEALTHY or DEGRADED (not UNHEALTHY)."""
        return self.status != HealthStatus.UNHEALTHY


class HealthChecker:
    """Orchestrates all health checks and produces aggregate status reports.

    Thresholds:
        - CPU > 90% → DEGRADED
        - Memory > 90% → DEGRADED
        - Disk > 95% → DEGRADED
        - DB query latency > 1s → DEGRADED; > 5s → UNHEALTHY
        - Any check UNHEALTHY → overall UNHEALTHY
        - Any check DEGRADED → overall DEGRADED

    Attributes:
        db_session_factory: Callable returning a SQLAlchemy session.
        model_loaded: Whether the ML model is loaded and ready.
        cpu_threshold_pct: CPU % above which status → DEGRADED.
        memory_threshold_pct: Memory % above which status → DEGRADED.
    """

    def __init__(
        self,
        db_session_factory=None,
        model_loaded: bool = False,
        cpu_threshold_pct: float = 90.0,
        memory_threshold_pct: float = 90.0,
    ) -> None:
        """Initialise the HealthChecker.

        Args:
            db_session_factory: Callable that returns a DB session (or None).
            model_loaded: Whether the ML model has been loaded.
            cpu_threshold_pct: CPU % threshold for DEGRADED status.
            memory_threshold_pct: Memory % threshold for DEGRADED status.
        """
        self.db_session_factory = db_session_factory
        self.model_loaded = model_loaded
        self.cpu_threshold_pct = cpu_threshold_pct
        self.memory_threshold_pct = memory_threshold_pct
        self._start_time = time.time()
        logger.info("HealthChecker initialised.")

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def check_database(self) -> CheckResult:
        """Verify database connectivity with a lightweight query.

        Returns:
            CheckResult with latency and row count detail.
        """
        t0 = time.perf_counter()
        if self.db_session_factory is None:
            return CheckResult(
                "database", HealthStatus.DEGRADED,
                {"message": "No DB session factory configured."},
            )
        try:
            db = self.db_session_factory()
            db.execute("SELECT 1")
            db.close()
            latency = (time.perf_counter() - t0) * 1000
            status = HealthStatus.HEALTHY if latency < 1000 else HealthStatus.DEGRADED
            return CheckResult(
                "database", status,
                {"message": "Connection OK", "query": "SELECT 1"},
                latency_ms=latency,
            )
        except Exception as exc:
            latency = (time.perf_counter() - t0) * 1000
            logger.error("Database health check failed: %s", exc)
            return CheckResult(
                "database", HealthStatus.UNHEALTHY,
                {"message": str(exc)},
                latency_ms=latency,
            )

    def check_ml_model(self) -> CheckResult:
        """Check whether the ML model is loaded and ready for inference.

        Returns:
            CheckResult indicating model readiness.
        """
        t0 = time.perf_counter()
        if self.model_loaded:
            return CheckResult(
                "ml_model", HealthStatus.HEALTHY,
                {"message": "Model loaded and ready.", "backend": "XGBoost"},
                latency_ms=(time.perf_counter() - t0) * 1000,
            )
        else:
            return CheckResult(
                "ml_model", HealthStatus.DEGRADED,
                {"message": "Model not yet loaded; using mock inference."},
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    def check_system_resources(self) -> CheckResult:
        """Check CPU, memory, and disk usage against thresholds.

        Returns:
            CheckResult with full system resource details.
        """
        t0 = time.perf_counter()
        try:
            cpu_pct     = psutil.cpu_percent(interval=0.1)
            mem         = psutil.virtual_memory()
            disk        = psutil.disk_usage("/")

            mem_pct  = mem.percent
            disk_pct = disk.percent

            issues = []
            if cpu_pct > self.cpu_threshold_pct:
                issues.append(f"High CPU: {cpu_pct:.1f}%")
            if mem_pct > self.memory_threshold_pct:
                issues.append(f"High memory: {mem_pct:.1f}%")
            if disk_pct > 95:
                issues.append(f"Low disk space: {disk_pct:.1f}% used")

            status = HealthStatus.HEALTHY if not issues else HealthStatus.DEGRADED

            return CheckResult(
                "system_resources", status,
                {
                    "cpu_percent": cpu_pct,
                    "memory_percent": mem_pct,
                    "memory_used_gb": round(mem.used / 1e9, 2),
                    "memory_available_gb": round(mem.available / 1e9, 2),
                    "disk_percent": disk_pct,
                    "disk_free_gb": round(disk.free / 1e9, 2),
                    "issues": issues,
                },
                latency_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as exc:
            return CheckResult(
                "system_resources", HealthStatus.DEGRADED,
                {"message": f"Resource check error: {exc}"},
            )

    def check_mlflow(self) -> CheckResult:
        """Verify MLflow tracking server connectivity.

        Returns:
            CheckResult indicating MLflow availability.
        """
        t0 = time.perf_counter()
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        try:
            import mlflow
            mlflow.set_tracking_uri(tracking_uri)
            experiments = mlflow.search_experiments()
            return CheckResult(
                "mlflow", HealthStatus.HEALTHY,
                {
                    "tracking_uri": tracking_uri,
                    "n_experiments": len(experiments),
                },
                latency_ms=(time.perf_counter() - t0) * 1000,
            )
        except ImportError:
            return CheckResult(
                "mlflow", HealthStatus.DEGRADED,
                {"message": "mlflow package not installed."},
            )
        except Exception as exc:
            return CheckResult(
                "mlflow", HealthStatus.DEGRADED,
                {"message": f"MLflow unavailable: {exc}", "tracking_uri": tracking_uri},
                latency_ms=(time.perf_counter() - t0) * 1000,
            )

    def check_dependencies(self) -> CheckResult:
        """Verify critical Python packages are importable.

        Returns:
            CheckResult listing available / missing packages.
        """
        REQUIRED = ["fastapi", "sqlalchemy", "xgboost", "shap", "pandas", "numpy", "mlflow"]
        missing = []
        available = []

        for pkg in REQUIRED:
            try:
                __import__(pkg)
                available.append(pkg)
            except ImportError:
                missing.append(pkg)

        status = HealthStatus.HEALTHY if not missing else HealthStatus.UNHEALTHY
        return CheckResult(
            "dependencies", status,
            {"available": available, "missing": missing},
        )

    # ------------------------------------------------------------------
    # Aggregate health report
    # ------------------------------------------------------------------

    def liveness(self) -> Dict[str, Any]:
        """Kubernetes liveness probe: is the process alive?

        Returns always HEALTHY unless the process is severely broken.
        """
        uptime = round(time.time() - self._start_time, 1)
        return {
            "status": HealthStatus.HEALTHY.value,
            "uptime_seconds": uptime,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def readiness(self) -> Dict[str, Any]:
        """Kubernetes readiness probe: is the service ready to handle traffic?

        Returns:
            Aggregated status and per-component check results.
        """
        checks: List[CheckResult] = [
            self.check_system_resources(),
            self.check_ml_model(),
            self.check_dependencies(),
            self.check_mlflow(),
        ]

        if self.db_session_factory is not None:
            checks.append(self.check_database())

        statuses = [c.status for c in checks]
        if HealthStatus.UNHEALTHY in statuses:
            overall = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY

        return {
            "status": overall.value,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "checks": [c.to_dict() for c in checks],
        }

    def full_health_report(self) -> Dict[str, Any]:
        """Complete health report combining liveness + readiness + details.

        Returns:
            Combined report suitable for /health/full endpoint.
        """
        liveness   = self.liveness()
        readiness  = self.readiness()
        return {
            **readiness,
            "liveness": liveness,
            "summary": {
                "total_checks": len(readiness["checks"]),
                "healthy": sum(1 for c in readiness["checks"] if c["status"] == "healthy"),
                "degraded": sum(1 for c in readiness["checks"] if c["status"] == "degraded"),
                "unhealthy": sum(1 for c in readiness["checks"] if c["status"] == "unhealthy"),
            },
        }


# ---------------------------------------------------------------------------
# Module-level singleton (configured at app startup)
# ---------------------------------------------------------------------------
_health_checker: Optional[HealthChecker] = None


def configure(
    db_session_factory=None,
    model_loaded: bool = False,
) -> HealthChecker:
    """Configure the global HealthChecker singleton.

    Args:
        db_session_factory: Callable returning a SQLAlchemy session.
        model_loaded: Whether the ML model artifact is loaded.

    Returns:
        The configured HealthChecker instance.
    """
    global _health_checker
    _health_checker = HealthChecker(
        db_session_factory=db_session_factory,
        model_loaded=model_loaded,
    )
    return _health_checker


def get_checker() -> HealthChecker:
    """Return the configured global HealthChecker.

    Returns:
        HealthChecker singleton.

    Raises:
        RuntimeError: If configure() has not been called.
    """
    if _health_checker is None:
        raise RuntimeError(
            "HealthChecker not configured. Call monitoring.health_checks.configure() at startup."
        )
    return _health_checker
