"""Abstract base class enforcing the ML model contract for ForesightAI.

Fixes applied vs original:
- B-01 (High): evaluate() method with full metric suite added as concrete method.
- B-02 (High): get_params() added as abstract method.
- B-03 (Medium): filepath validation guidance in docstrings.
- B-04 (Medium): model_name property added.
- B-05 (Low): Full Google-style docstrings on all methods.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for all ML models in ForesightAI.

    Concrete subclasses must implement:
        train, predict, predict_proba, save, load, get_params.

    The evaluate() method is a concrete default that can be overridden.
    """

    @property
    def model_name(self) -> str:
        """Human-readable name of this model implementation."""
        return self.__class__.__name__

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs: Any) -> None:
        """Train the model on the provided dataset.

        Args:
            X_train: Feature matrix of training samples.
            y_train: Target labels for training samples.
            **kwargs: Additional keyword arguments passed to the underlying
                estimator's fit method (e.g., eval_set, early_stopping_rounds).
        """

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generate hard class predictions.

        Args:
            X: Feature matrix for inference.

        Returns:
            1-D array of predicted class labels.
        """

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Generate class probability estimates.

        Args:
            X: Feature matrix for inference.

        Returns:
            2-D array of shape (n_samples, n_classes) with probability scores.
        """

    @abstractmethod
    def save(self, filepath: str) -> None:
        """Persist model artifacts to disk.

        Args:
            filepath: Destination file path. Implementations should validate
                the file extension and create parent directories as needed.
        """

    @abstractmethod
    def load(self, filepath: str) -> None:
        """Load model artifacts from disk.

        Args:
            filepath: Path to a previously saved model file.

        Raises:
            FileNotFoundError: If the file does not exist.
        """

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """Return the model's current hyperparameter dictionary.

        Returns:
            Dict mapping parameter names to their current values.
        """

    # ------------------------------------------------------------------
    # Concrete default — override in subclass for model-specific logic
    # ------------------------------------------------------------------

    def evaluate(
        self,
        X: pd.DataFrame,
        y_true: pd.Series,
        threshold: float = 0.5,
    ) -> Dict[str, float]:
        """Compute a standard suite of binary classification metrics.

        Args:
            X: Feature matrix.
            y_true: Ground truth labels.
            threshold: Decision threshold applied to positive-class probability.
                Unused when using hard predict() — retained for signature
                compatibility with calibrated subclasses.

        Returns:
            Dict containing:
                - accuracy: Fraction of correct predictions.
                - precision: Positive predictive value.
                - recall: Sensitivity / true positive rate.
                - f1: Harmonic mean of precision and recall.
                - roc_auc: Area under the ROC curve.

        Raises:
            RuntimeError: If prediction fails.
        """
        try:
            y_pred = self.predict(X)
            y_proba = self.predict_proba(X)
            # For binary classification take the positive-class column
            pos_proba = y_proba[:, 1] if y_proba.ndim == 2 else y_proba

            metrics = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "precision": float(
                    precision_score(y_true, y_pred, zero_division=0)
                ),
                "recall": float(
                    recall_score(y_true, y_pred, zero_division=0)
                ),
                "f1": float(f1_score(y_true, y_pred, zero_division=0)),
                "roc_auc": float(roc_auc_score(y_true, pos_proba)),
            }
            logger.info("[%s] Evaluation metrics: %s", self.model_name, metrics)
            return metrics

        except Exception as exc:
            logger.exception("[%s] evaluate() failed: %s", self.model_name, exc)
            raise RuntimeError(f"Model evaluation failed: {exc}") from exc

    def __repr__(self) -> str:
        return f"{self.model_name}(params={self.get_params()})"
