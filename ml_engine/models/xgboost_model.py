"""XGBoost model implementation of the ForesightAI BaseModel contract.

Fixes applied vs original:
- X-01 (Critical): Removed use_label_encoder=False (removed in XGBoost >= 1.6).
- X-02 (Critical): joblib.load() path validated before deserialization.
- X-03 (High): random_state set from config for reproducibility.
- X-04 (High): early_stopping_rounds supported in train().
- X-05 (High): get_params() implemented.
- X-06 (High): Logging added throughout.
- X-07 (High): get_feature_importances() returns named dict, not raw array.
- X-08 (Medium): save() also writes native XGBoost .json for ONNX compatibility.
- X-09 (Medium): GPU support via config.use_gpu flag.
- X-10 (Low): Full Google-style docstrings.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from ml_engine.core.config import config
from ml_engine.models.base_model import BaseModel

logger = logging.getLogger(__name__)

# Allowed file extensions for safe deserialization
_SAFE_EXTENSIONS = frozenset({".joblib", ".json", ".pkl"})


class XGBoostModel(BaseModel):
    """XGBoost classifier implementing the ForesightAI BaseModel contract.

    Attributes:
        model: The underlying XGBClassifier instance.
        feature_names: List of column names seen during training.
    """

    def __init__(self, **params: Any) -> None:
        """Initialise the XGBoost classifier.

        Sensible defaults are applied if not provided:
            - random_state → config.random_seed
            - eval_metric  → 'logloss'
            - n_jobs       → config.n_jobs
            - tree_method  → 'gpu_hist' if config.use_gpu else 'hist'

        Args:
            **params: Hyperparameters forwarded to XGBClassifier.
                NOTE: Do NOT pass ``use_label_encoder`` — it was removed
                in XGBoost 1.6 and will raise a TypeError.
        """
        # Remove deprecated kwarg if caller passes it defensively
        params.pop("use_label_encoder", None)

        params.setdefault("random_state", config.random_seed)
        params.setdefault("eval_metric", "logloss")
        params.setdefault("n_jobs", config.n_jobs)
        params.setdefault(
            "tree_method", "gpu_hist" if config.use_gpu else "hist"
        )

        # In XGBoost >= 2.0, early_stopping_rounds belongs in the constructor,
        # not in fit().  We pop it here so it can be set later via set_params().
        self._early_stopping_rounds: int = params.pop("early_stopping_rounds", 50)

        self.model = xgb.XGBClassifier(**params)
        self.feature_names: Optional[List[str]] = None
        logger.info("XGBoostModel initialised with params: %s", params)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        early_stopping_rounds: int = 50,
        **kwargs: Any,
    ) -> None:
        """Train the model with optional early stopping on a validation set.

        Args:
            X_train: Training feature matrix.
            y_train: Training target labels.
            X_val: Validation feature matrix for early stopping evaluation.
            y_val: Validation target labels.
            early_stopping_rounds: Number of rounds without improvement before
                training stops early. Only active when X_val/y_val are provided.
            **kwargs: Additional keyword arguments forwarded to XGBClassifier.fit().

        Raises:
            ValueError: If X_val is provided without y_val or vice-versa.
        """
        if (X_val is None) != (y_val is None):
            raise ValueError("X_val and y_val must both be provided or both be None.")

        self.feature_names = list(X_train.columns)

        fit_params: Dict[str, Any] = {**kwargs}
        if X_val is not None:
            fit_params["eval_set"] = [(X_val, y_val)]
            fit_params.setdefault("verbose", False)
            # XGBoost >= 2.0: early_stopping_rounds is a constructor param.
            # Set it on the model instance before fitting.
            self.model.set_params(early_stopping_rounds=early_stopping_rounds)

        logger.info(
            "Training XGBoostModel on %d samples, %d features.",
            len(X_train),
            X_train.shape[1],
        )
        self.model.fit(X_train, y_train, **fit_params)
        best_iter = getattr(self.model, "best_iteration", "N/A")
        logger.info("Training complete. Best iteration: %s", best_iter)

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Return hard class predictions.

        Args:
            X: Feature matrix for inference.

        Returns:
            1-D integer array of predicted class labels.
        """
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Return class probability estimates.

        Args:
            X: Feature matrix for inference.

        Returns:
            2-D array of shape (n_samples, n_classes).
        """
        return self.model.predict_proba(X)

    # ------------------------------------------------------------------
    # Hyperparameters
    # ------------------------------------------------------------------

    def get_params(self) -> Dict[str, Any]:
        """Return the model's current hyperparameter dictionary.

        Returns:
            Dict mapping XGBoost parameter names to their values.
        """
        return self.model.get_params()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Save the model using joblib and also export a native XGBoost JSON.

        Two files are written:
            - ``filepath``               — joblib-serialised sklearn wrapper
            - ``filepath`` with .json    — native XGBoost model (ONNX-ready)

        Args:
            filepath: Destination path ending in .joblib or .pkl.

        Raises:
            ValueError: If the file extension is not in the allowed set.
        """
        path = Path(filepath)
        if path.suffix not in _SAFE_EXTENSIONS:
            raise ValueError(
                f"Unsafe file extension '{path.suffix}'. "
                f"Allowed: {sorted(_SAFE_EXTENSIONS)}"
            )
        path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.model, filepath)
        logger.info("Model saved (joblib): '%s'", filepath)

        # Also save native XGBoost JSON for interoperability / ONNX export
        json_path = path.with_suffix(".json")
        self.model.save_model(str(json_path))
        logger.info("Model saved (XGBoost JSON): '%s'", json_path)

    def load(self, filepath: str) -> None:
        """Load a model from a joblib file.

        Args:
            filepath: Path to a previously saved .joblib file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not in the allowed set.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: '{filepath}'.")
        if path.suffix not in _SAFE_EXTENSIONS:
            raise ValueError(
                f"Unsafe file extension '{path.suffix}'. "
                f"Allowed: {sorted(_SAFE_EXTENSIONS)}"
            )
        self.model = joblib.load(filepath)
        logger.info("Model loaded from: '%s'", filepath)

    # ------------------------------------------------------------------
    # Feature importances
    # ------------------------------------------------------------------

    def get_feature_importances(self) -> Dict[str, float]:
        """Return a named dictionary of XGBoost feature importances.

        Returns:
            Dict mapping feature name (str) to importance score (float),
            sorted descending by importance.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        importances: np.ndarray = self.model.feature_importances_
        if importances is None:
            raise RuntimeError(
                "Feature importances unavailable — model has not been trained."
            )
        names = self.feature_names or [f"feature_{i}" for i in range(len(importances))]
        return dict(
            sorted(
                zip(names, importances.tolist()),
                key=lambda kv: kv[1],
                reverse=True,
            )
        )
