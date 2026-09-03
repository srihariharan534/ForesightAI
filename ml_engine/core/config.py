"""Central configuration for the ML Engine.

All settings can be overridden via environment variables prefixed with ML_
(e.g. ML_RANDOM_SEED=0) or via a .env file in the project root.
"""
import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class MLEngineConfig(BaseSettings):
    """Configuration for the ML Engine, loaded from environment variables.

    Attributes:
        model_registry_uri: MLflow tracking server URI.
        experiment_name: Name of the MLflow experiment.
        model_version: Semantic version tag for the model.
        random_seed: Global random seed for reproducibility.
        model_artifact_dir: Local directory for saved model artifacts.
        n_jobs: Parallel workers for sklearn-compatible estimators (-1 = all cores).
        log_level: Python logging level string.
        batch_size: Default batch size for batch inference.
        use_gpu: Whether to enable GPU acceleration where supported.
    """

    model_config = SettingsConfigDict(
        env_prefix="ML_",
        env_file=".env",
        extra="ignore",
    )

    # MLflow / Registry
    model_registry_uri: str = "sqlite:///mlflow.db"
    experiment_name: str = "ForesightAI_Default"
    model_version: str = "1.0.0"

    # Reproducibility
    random_seed: int = 42

    # Paths
    model_artifact_dir: Path = Path("models/artifacts")

    # Performance
    n_jobs: int = -1
    batch_size: int = 256
    use_gpu: bool = False

    # Logging
    log_level: str = "INFO"


config = MLEngineConfig()
