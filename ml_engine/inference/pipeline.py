"""Production inference pipeline: load artifacts, validate input, predict + explain.

Usage::

    from ml_engine.inference.pipeline import InferencePipeline

    pipeline = InferencePipeline(
        model_path="models/artifacts/xgboost_v1.0.0.joblib",
        preprocessor_path="models/artifacts/preprocessor_v1.0.0.joblib",
    )
    result = pipeline.predict_single({"age": 35, "income": 60000, "category": "A"})
    batch = pipeline.predict_batch([...])
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from ml_engine.data.preprocessor import DataPreprocessor
from ml_engine.explainability.explainer import ModelExplainer
from ml_engine.models.xgboost_model import XGBoostModel

logger = logging.getLogger(__name__)


class InferencePipeline:
    """Loads a trained model + preprocessor and runs safe, validated inference.

    Attributes:
        model: Loaded XGBoostModel.
        preprocessor: Loaded (fitted) DataPreprocessor.
        explainer: Optional SHAP ModelExplainer (None if not enabled).
    """

    def __init__(
        self,
        model_path: str,
        preprocessor_path: str,
        enable_explanations: bool = True,
    ) -> None:
        """Load model and preprocessor artifacts from disk.

        Args:
            model_path: Path to the saved .joblib model file.
            preprocessor_path: Path to the saved .joblib preprocessor file.
            enable_explanations: Whether to initialise the SHAP explainer.
                Disable for maximum throughput in high-QPS scenarios.

        Raises:
            FileNotFoundError: If either artifact path does not exist.
        """
        logger.info("Loading inference pipeline artifacts…")
        self.model = XGBoostModel()
        self.model.load(model_path)

        self.preprocessor = DataPreprocessor.load(preprocessor_path)

        self.explainer: Optional[ModelExplainer] = None
        if enable_explanations:
            try:
                self.explainer = ModelExplainer(self.model.model)
                logger.info("SHAP explainer initialised.")
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "SHAP explainer could not be initialised (%s). "
                    "Explanations will be disabled.",
                    exc,
                )

        logger.info(
            "InferencePipeline ready — model='%s', preprocessor='%s'.",
            model_path,
            preprocessor_path,
        )

    # ------------------------------------------------------------------
    # Single prediction
    # ------------------------------------------------------------------

    def predict_single(
        self,
        features: Dict[str, Any],
        explain: bool = True,
    ) -> Dict[str, Any]:
        """Run inference and optionally explain a single feature dictionary.

        Args:
            features: Dict mapping feature names to their raw (unprocessed) values.
            explain: Whether to include SHAP values in the response.
                Ignored if enable_explanations=False at init.

        Returns:
            Dict containing:
                - ``predicted_class`` (int): Hard class label.
                - ``confidence_score`` (float): Probability of the predicted class.
                - ``probabilities`` (List[float]): Full probability vector.
                - ``shap_explanation`` (Dict | None): SHAP output or None.

        Raises:
            ValueError: If features is empty.
            RuntimeError: If preprocessing or inference fails.
        """
        if not features:
            raise ValueError("features dict must not be empty.")

        try:
            df = pd.DataFrame([features])
            X = self.preprocessor.transform(df)
            proba = self.model.predict_proba(X)[0]
            label = int(self.model.predict(X)[0])

            shap_result: Optional[Dict[str, Any]] = None
            if explain and self.explainer is not None:
                shap_result = self.explainer.explain_instance(X)

            result = {
                "predicted_class": label,
                "confidence_score": float(max(proba)),
                "probabilities": proba.tolist(),
                "shap_explanation": shap_result,
            }
            logger.debug("Single prediction: class=%d, confidence=%.4f", label, max(proba))
            return result

        except Exception as exc:
            logger.exception("predict_single() failed: %s", exc)
            raise RuntimeError(f"Inference failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Batch prediction
    # ------------------------------------------------------------------

    def predict_batch(
        self,
        records: List[Dict[str, Any]],
        explain: bool = False,
    ) -> List[Dict[str, Any]]:
        """Run inference on a list of feature dictionaries.

        Args:
            records: List of raw feature dicts (same schema as predict_single).
            explain: Whether to include per-instance SHAP values.
                Disabled by default for throughput — SHAP is expensive at scale.

        Returns:
            List of prediction dicts (same schema as predict_single).

        Raises:
            ValueError: If records is empty.
            RuntimeError: If preprocessing or inference fails.
        """
        if not records:
            raise ValueError("records list must not be empty.")

        try:
            df = pd.DataFrame(records)
            X = self.preprocessor.transform(df)
            probas = self.model.predict_proba(X)
            labels = self.model.predict(X)

            shap_results: Optional[List[Dict[str, Any]]] = None
            if explain and self.explainer is not None:
                shap_results = self.explainer.explain_batch(X)

            output: List[Dict[str, Any]] = []
            for i, (label, proba) in enumerate(zip(labels, probas)):
                output.append(
                    {
                        "predicted_class": int(label),
                        "confidence_score": float(max(proba)),
                        "probabilities": proba.tolist(),
                        "shap_explanation": shap_results[i] if shap_results else None,
                    }
                )

            logger.info(
                "Batch prediction complete — %d records processed.", len(output)
            )
            return output

        except Exception as exc:
            logger.exception("predict_batch() failed: %s", exc)
            raise RuntimeError(f"Batch inference failed: {exc}") from exc
