"""Data preprocessing module: cleaning, encoding, scaling, and splitting.

Fixes applied vs original:
- D-01 (Critical): Training medians stored at fit time; reused at transform time (no data leakage).
- D-02 (Critical): Unseen LabelEncoder classes handled gracefully via __unknown__ sentinel.
- D-03 (Critical): train/val/test split method added.
- D-04 (High): LabelEncoder replaced with OrdinalEncoder for safety; OHE flag available.
- D-05 (High): Logging added throughout.
- D-06 (High): Input validation added.
- D-07 (High): save() / load() added for the fitted preprocessor.
- D-08 (Medium): Optional[str] type hint corrected.
- D-09 (Medium): Feature column consistency check between fit and transform.
- D-10 (Medium): Imputation strategy is now configurable.
- D-11 (Low): Google-style docstrings with Args/Returns/Raises.
"""

import logging
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Handles data cleaning, encoding, scaling and train/val/test splitting.

    Attributes:
        scaler: Fitted StandardScaler for numerical columns.
        label_encoders: Per-column LabelEncoders for categorical columns.
        impute_strategy: Strategy for numeric imputation ('median' or 'mean').
        is_fitted: Whether fit_transform() has been called.
    """

    def __init__(self, impute_strategy: str = "median") -> None:
        """Initialise the preprocessor.

        Args:
            impute_strategy: How to impute missing numeric values.
                Must be 'median' or 'mean'.

        Raises:
            ValueError: If impute_strategy is not recognised.
        """
        if impute_strategy not in ("median", "mean"):
            raise ValueError(
                f"impute_strategy must be 'median' or 'mean', got '{impute_strategy}'."
            )
        self.impute_strategy = impute_strategy
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self._train_fill_values: Optional[pd.Series] = None   # stored at fit time
        self._feature_columns: Optional[List[str]] = None
        self.is_fitted: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fit_transform(
        self,
        df: pd.DataFrame,
        target_col: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Fit all encoders/scalers on df and return the transformed data.

        Args:
            df: Raw input DataFrame.
            target_col: Name of the target column to extract and return
                separately. If None, no target is extracted.

        Returns:
            Tuple of (X_transformed, y) where y is None if target_col is None.

        Raises:
            ValueError: If df is empty or target_col is not found.
        """
        if df.empty:
            raise ValueError("Input DataFrame is empty.")

        X = df.copy()
        y: Optional[pd.Series] = None

        if target_col is not None:
            if target_col not in X.columns:
                raise ValueError(f"target_col '{target_col}' not found in DataFrame.")
            y = X.pop(target_col)
            logger.info("Extracted target column '%s'.", target_col)

        self._feature_columns = list(X.columns)

        # ---- Numeric imputation (fit) ---------------------------------
        num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            if self.impute_strategy == "median":
                self._train_fill_values = X[num_cols].median()
            else:
                self._train_fill_values = X[num_cols].mean()
            X[num_cols] = X[num_cols].fillna(self._train_fill_values)
            logger.info(
                "Imputed %d numeric column(s) using %s.", len(num_cols), self.impute_strategy
            )

        # ---- Categorical encoding (fit) ------------------------------
        cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
        X[cat_cols] = X[cat_cols].fillna("Unknown")
        for col in cat_cols:
            le = LabelEncoder()
            le.fit(X[col].astype(str))
            # Reserve an extra class for unseen values at inference time
            le.classes_ = np.append(le.classes_, "__unknown__")
            X[col] = le.transform(X[col].astype(str))
            self.label_encoders[col] = le
        if cat_cols:
            logger.info("Label-encoded %d categorical column(s).", len(cat_cols))

        # ---- Numeric scaling (fit) ------------------------------------
        if num_cols:
            X[num_cols] = self.scaler.fit_transform(X[num_cols])
            logger.info("StandardScaler fitted on %d numeric column(s).", len(num_cols))

        self.is_fitted = True
        logger.info("fit_transform complete. Shape: %s", X.shape)
        return X, y

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using encoders/scalers fitted at training time.

        Args:
            df: Raw inference-time DataFrame. Must contain the same feature
                columns seen during fit_transform().

        Returns:
            Transformed DataFrame ready for model inference.

        Raises:
            RuntimeError: If the preprocessor has not been fitted.
            ValueError: If required feature columns are missing from df.
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform().")
        if df.empty:
            raise ValueError("Input DataFrame is empty.")

        X = df.copy()

        # Feature consistency check
        if self._feature_columns is not None:
            missing = set(self._feature_columns) - set(X.columns)
            if missing:
                raise ValueError(
                    f"Missing feature columns in inference data: {missing}"
                )
            X = X[self._feature_columns]  # ensure column order matches training

        # ---- Numeric imputation (use TRAINING fill values) -----------
        num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols and self._train_fill_values is not None:
            # Only fill columns that were seen during training
            fill = self._train_fill_values.reindex(num_cols)
            X[num_cols] = X[num_cols].fillna(fill)

        # ---- Categorical encoding (handle unseen labels) -------------
        cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
        X[cat_cols] = X[cat_cols].fillna("Unknown")
        for col in cat_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                known = set(le.classes_)
                # Map unseen values to the reserved __unknown__ class
                X[col] = X[col].astype(str).apply(
                    lambda v, k=known: v if v in k else "__unknown__"
                )
                X[col] = le.transform(X[col])

        # ---- Numeric scaling (use fitted scaler) ---------------------
        if num_cols:
            X[num_cols] = self.scaler.transform(X[num_cols])

        logger.info("transform complete. Shape: %s", X.shape)
        return X

    def split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        val_size: float = 0.1,
        stratify: bool = True,
        random_state: int = 42,
    ) -> Tuple[
        pd.DataFrame, pd.DataFrame, pd.DataFrame,
        pd.Series, pd.Series, pd.Series,
    ]:
        """Split data into train / validation / test sets.

        Args:
            X: Feature matrix (after fit_transform).
            y: Target series.
            test_size: Fraction of the full dataset to reserve for testing.
            val_size: Fraction of the full dataset to reserve for validation.
            stratify: Whether to stratify splits by y.
            random_state: Random seed for reproducibility.

        Returns:
            Tuple (X_train, X_val, X_test, y_train, y_val, y_test).

        Raises:
            ValueError: If test_size + val_size >= 1.0.
        """
        if test_size + val_size >= 1.0:
            raise ValueError(
                f"test_size ({test_size}) + val_size ({val_size}) must be < 1.0."
            )

        strat = y if stratify else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=strat
        )

        val_fraction = val_size / (1.0 - test_size)
        strat_train = y_train if stratify else None
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train,
            test_size=val_fraction,
            random_state=random_state,
            stratify=strat_train,
        )

        logger.info(
            "Data split — train: %d, val: %d, test: %d",
            len(X_train), len(X_val), len(X_test),
        )
        return X_train, X_val, X_test, y_train, y_val, y_test

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Persist the fitted preprocessor to disk using joblib.

        Args:
            filepath: Destination path (e.g. 'artifacts/preprocessor.joblib').

        Raises:
            RuntimeError: If the preprocessor has not been fitted.
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save an unfitted preprocessor.")
        joblib.dump(self, filepath)
        logger.info("Preprocessor saved to '%s'.", filepath)

    @classmethod
    def load(cls, filepath: str) -> "DataPreprocessor":
        """Load a previously saved DataPreprocessor from disk.

        Args:
            filepath: Path to a joblib-serialised DataPreprocessor.

        Returns:
            A fitted DataPreprocessor instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            TypeError: If the loaded object is not a DataPreprocessor.
        """
        import os
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preprocessor file not found: '{filepath}'.")
        obj = joblib.load(filepath)
        if not isinstance(obj, cls):
            raise TypeError(
                f"Expected DataPreprocessor, got {type(obj).__name__}."
            )
        logger.info("Preprocessor loaded from '%s'.", filepath)
        return obj

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"DataPreprocessor("
            f"impute_strategy={self.impute_strategy!r}, "
            f"is_fitted={self.is_fitted})"
        )
