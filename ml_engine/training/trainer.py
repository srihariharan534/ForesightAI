"""End-to-end training pipeline for ForesightAI.

Usage (CLI)::

    python -m ml_engine.training.trainer \\
        --data-path datasets/sample/sample_data.csv \\
        --target-col target

Usage (Python)::

    from ml_engine.training.trainer import train
    model = train("datasets/sample/sample_data.csv", target_col="target")
"""

import argparse
import logging
import random
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from ml_engine.core.config import config
from ml_engine.data.preprocessor import DataPreprocessor
from ml_engine.mlops.tracker import MLOpsTracker
from ml_engine.models.xgboost_model import XGBoostModel

logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def set_global_seed(seed: int) -> None:
    """Set all global random seeds for full reproducibility.

    Args:
        seed: Integer seed value.
    """
    random.seed(seed)
    np.random.seed(seed)
    logger.info("Global random seed set to %d.", seed)


def train(
    data_path: str,
    target_col: str,
    model_output_dir: Optional[str] = None,
    test_size: float = 0.2,
    val_size: float = 0.1,
    xgb_params: Optional[Dict[str, Any]] = None,
    run_name: Optional[str] = None,
) -> XGBoostModel:
    """Run the complete train → evaluate → log → save pipeline.

    Steps performed:
        1. Set global random seeds.
        2. Load CSV dataset.
        3. Fit preprocessor (with train/val/test split).
        4. Train XGBoost with early stopping on the validation set.
        5. Evaluate on the held-out test set.
        6. Log all params, metrics, and artifacts to MLflow.
        7. Save preprocessor and model to disk.

    Args:
        data_path: Path to the CSV training dataset.
        target_col: Name of the target column.
        model_output_dir: Directory where model artifacts are saved.
            Defaults to config.model_artifact_dir.
        test_size: Fraction of data reserved for the test set.
        val_size: Fraction of data reserved for the validation set.
        xgb_params: Optional XGBoost hyperparameter overrides.
        run_name: Optional MLflow run name.

    Returns:
        The trained XGBoostModel instance.

    Raises:
        FileNotFoundError: If data_path does not exist.
        ValueError: If the dataset is empty or target_col is missing.
    """
    set_global_seed(config.random_seed)

    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Dataset not found: '{data_path}'.")

    logger.info("Loading dataset from '%s'.", data_path)
    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError(f"Dataset is empty: '{data_path}'.")
    logger.info("Dataset loaded — %d rows × %d columns.", *df.shape)

    if target_col not in df.columns:
        raise ValueError(
            f"Target column '{target_col}' not found. "
            f"Available: {list(df.columns)}"
        )

    # ------------------------------------------------------------------
    # 2. Preprocess + split
    # ------------------------------------------------------------------
    preprocessor = DataPreprocessor()
    X, y = preprocessor.fit_transform(df, target_col=target_col)
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split(
        X, y, test_size=test_size, val_size=val_size
    )

    # ------------------------------------------------------------------
    # 3. Build model
    # ------------------------------------------------------------------
    model = XGBoostModel(**(xgb_params or {}))
    tracker = MLOpsTracker()

    # ------------------------------------------------------------------
    # 4. Train + evaluate + log
    # ------------------------------------------------------------------
    with tracker.run(run_name=run_name or "xgboost_training") as active_run:
        run_id = active_run.info.run_id
        logger.info("MLflow run_id: %s", run_id)

        # Log hyperparameters
        tracker.log_params({
            **model.get_params(),
            "test_size": test_size,
            "val_size": val_size,
            "random_seed": config.random_seed,
            "dataset": data_file.name,
        })
        tracker.set_tags({
            "model_version": config.model_version,
            "dataset_rows": str(len(df)),
        })

        # Train
        model.train(X_train, y_train, X_val=X_val, y_val=y_val)

        # Evaluate on all splits
        train_metrics = model.evaluate(X_train, y_train)
        val_metrics = model.evaluate(X_val, y_val)
        test_metrics = model.evaluate(X_test, y_test)

        # Prefix metrics by split for MLflow clarity
        all_metrics = {
            **{f"train_{k}": v for k, v in train_metrics.items()},
            **{f"val_{k}": v for k, v in val_metrics.items()},
            **{f"test_{k}": v for k, v in test_metrics.items()},
        }
        tracker.log_metrics(all_metrics)
        logger.info("Test metrics: %s", test_metrics)

        # ------------------------------------------------------------------
        # 5. Save artifacts
        # ------------------------------------------------------------------
        output_dir = Path(model_output_dir or config.model_artifact_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        model_path = str(
            output_dir / f"xgboost_v{config.model_version}_run_{run_id[:8]}.joblib"
        )
        preprocessor_path = str(
            output_dir / f"preprocessor_v{config.model_version}_run_{run_id[:8]}.joblib"
        )

        model.save(model_path)
        preprocessor.save(preprocessor_path)

        tracker.log_artifact(model_path, "model")
        tracker.log_artifact(preprocessor_path, "preprocessor")
        tracker.log_model(model.model, "xgboost_mlflow")

    logger.info("Training pipeline complete. Run ID: %s", run_id)
    return model


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ForesightAI — XGBoost Training Pipeline"
    )
    parser.add_argument("--data-path", required=True, help="Path to training CSV.")
    parser.add_argument("--target-col", required=True, help="Name of target column.")
    parser.add_argument("--output-dir", default=None, help="Model artifact output dir.")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--val-size", type=float, default=0.1)
    parser.add_argument("--run-name", default=None)
    parser.add_argument("--n-estimators", type=int, default=300)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    train(
        data_path=args.data_path,
        target_col=args.target_col,
        model_output_dir=args.output_dir,
        test_size=args.test_size,
        val_size=args.val_size,
        run_name=args.run_name,
        xgb_params={
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "learning_rate": args.learning_rate,
        },
    )
