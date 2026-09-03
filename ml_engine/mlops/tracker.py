"""MLOps experiment tracking wrapper around MLflow.

Fixes applied vs original:
- M-01 (High): start_run() documented; context-manager pattern enforced via run().
- M-02 (High): run() is a @contextmanager — runs are always closed on exit.
- M-03 (High): xgboost imported at module level with try/except guard.
- M-04 (High): log_artifact() and set_tags() methods added.
- M-05 (High): Logging added throughout.
- M-06 (Medium): set_tags() wrapper added.
- M-07 (Medium): mlflow.set_tracking_uri() called only once (class-level flag).
- M-08 (Low): Type hints and Google-style docstrings added.
"""

import logging
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional

import mlflow
import mlflow.sklearn

try:
    import mlflow.xgboost
    import xgboost as _xgb
    _XGB_AVAILABLE = True
except ImportError:
    _XGB_AVAILABLE = False

from ml_engine.core.config import config

logger = logging.getLogger(__name__)


class MLOpsTracker:
    """Reproducible experiment tracker wrapping MLflow.

    Usage::

        tracker = MLOpsTracker()
        with tracker.run(run_name="xgboost_v1") as active_run:
            tracker.log_params({"n_estimators": 200})
            tracker.log_metrics({"roc_auc": 0.97})
            tracker.log_model(model.model, "xgboost_model")
            tracker.log_artifact("artifacts/preprocessor.joblib", "preprocessor")
    """

    _initialized: bool = False

    def __init__(self) -> None:
        """Configure MLflow tracking URI and experiment (once per process)."""
        if not MLOpsTracker._initialized:
            mlflow.set_tracking_uri(config.model_registry_uri)
            mlflow.set_experiment(config.experiment_name)
            MLOpsTracker._initialized = True
            logger.info(
                "MLflow configured — uri='%s', experiment='%s'.",
                config.model_registry_uri,
                config.experiment_name,
            )

    # ------------------------------------------------------------------
    # Run lifecycle
    # ------------------------------------------------------------------

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> Generator:
        """Context manager for a single MLflow run.

        The run is guaranteed to be ended (even on exception) when the
        ``with`` block exits.

        Args:
            run_name: Optional human-readable label for this run.

        Yields:
            mlflow.ActiveRun: The active MLflow run object (contains run_id etc.).

        Example::

            with tracker.run("experiment_42") as run:
                print(run.info.run_id)
        """
        logger.info("Starting MLflow run: '%s'.", run_name)
        with mlflow.start_run(run_name=run_name) as active_run:
            logger.info("MLflow run started — run_id=%s.", active_run.info.run_id)
            yield active_run
        logger.info("MLflow run ended: '%s'.", run_name)

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log a dictionary of hyperparameters to the active run.

        Args:
            params: Dict mapping parameter names to their values.
        """
        mlflow.log_params(params)
        logger.debug("Logged %d param(s).", len(params))

    def log_metrics(self, metrics: Dict[str, float]) -> None:
        """Log a dictionary of evaluation metrics to the active run.

        Args:
            metrics: Dict mapping metric names to float values.
        """
        mlflow.log_metrics(metrics)
        logger.info("Metrics logged: %s", metrics)

    def set_tags(self, tags: Dict[str, str]) -> None:
        """Tag the active run with key-value metadata.

        Useful for recording dataset version, git commit hash, model stage, etc.

        Args:
            tags: Dict mapping tag keys to string values.
        """
        mlflow.set_tags(tags)
        logger.debug("Tags set: %s", tags)

    def log_artifact(
        self,
        local_path: str,
        artifact_path: Optional[str] = None,
    ) -> None:
        """Upload a local file or directory as a run artifact.

        Args:
            local_path: Path to the local file or directory to upload.
            artifact_path: Optional sub-directory within the artifact store.
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.info("Artifact logged: '%s' → '%s'.", local_path, artifact_path)

    def log_model(self, model: Any, artifact_path: str) -> None:
        """Log a trained model to the MLflow artifact store.

        Automatically selects mlflow.xgboost or mlflow.sklearn based on type.

        Args:
            model: Trained model instance (raw estimator, not the BaseModel wrapper).
            artifact_path: Sub-path within the run's artifact store.
        """
        if _XGB_AVAILABLE and isinstance(
            model, (_xgb.XGBModel, _xgb.core.Booster)
        ):
            mlflow.xgboost.log_model(model, artifact_path)
            logger.info("XGBoost model logged to '%s'.", artifact_path)
        else:
            mlflow.sklearn.log_model(model, artifact_path)
            logger.info("sklearn model logged to '%s'.", artifact_path)
