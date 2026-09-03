"""Comprehensive unit + integration tests for the ml_engine package.

Run with::

    pytest tests/test_ml_engine.py -v --tb=short

Or with coverage::

    pytest tests/test_ml_engine.py -v --cov=ml_engine --cov-report=term-missing
"""

import numpy as np
import pandas as pd
import pytest

from ml_engine.data.preprocessor import DataPreprocessor
from ml_engine.models.xgboost_model import XGBoostModel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sample_df() -> pd.DataFrame:
    """100-row synthetic DataFrame matching the ForesightAI schema."""
    rng = np.random.default_rng(42)
    n = 100
    return pd.DataFrame(
        {
            "age": rng.integers(18, 70, n),
            "income": rng.normal(55_000, 10_000, n).clip(10_000, 150_000),
            "credit_score": rng.integers(300, 850, n),
            "employment_type": rng.choice(["Full-Time", "Part-Time", "Self-Employed"], n),
            "region": rng.choice(["North", "South", "East", "West"], n),
            "target": rng.integers(0, 2, n),
        }
    )


@pytest.fixture(scope="module")
def fitted_preprocessor(sample_df):
    pre = DataPreprocessor()
    pre.fit_transform(sample_df, target_col="target")
    return pre


@pytest.fixture(scope="module")
def transformed_data(sample_df):
    pre = DataPreprocessor()
    X, y = pre.fit_transform(sample_df, target_col="target")
    return pre, X, y


# ---------------------------------------------------------------------------
# DataPreprocessor — init & validation
# ---------------------------------------------------------------------------

class TestDataPreprocessorInit:
    def test_default_strategy(self):
        pre = DataPreprocessor()
        assert pre.impute_strategy == "median"
        assert not pre.is_fitted

    def test_mean_strategy(self):
        pre = DataPreprocessor(impute_strategy="mean")
        assert pre.impute_strategy == "mean"

    def test_invalid_strategy(self):
        with pytest.raises(ValueError, match="impute_strategy"):
            DataPreprocessor(impute_strategy="mode")

    def test_repr(self):
        pre = DataPreprocessor()
        assert "DataPreprocessor" in repr(pre)


# ---------------------------------------------------------------------------
# DataPreprocessor — fit_transform
# ---------------------------------------------------------------------------

class TestFitTransform:
    def test_shape_preserved(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        assert X.shape[0] == len(sample_df)
        assert "target" not in X.columns

    def test_target_extracted(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        assert y is not None
        assert len(y) == len(sample_df)

    def test_no_nulls_after_fit_transform(self, sample_df):
        pre = DataPreprocessor()
        X, _ = pre.fit_transform(sample_df, target_col="target")
        assert not X.isnull().any().any()

    def test_is_fitted_flag(self, sample_df):
        pre = DataPreprocessor()
        assert not pre.is_fitted
        pre.fit_transform(sample_df, target_col="target")
        assert pre.is_fitted

    def test_empty_df_raises(self):
        pre = DataPreprocessor()
        with pytest.raises(ValueError, match="empty"):
            pre.fit_transform(pd.DataFrame(), target_col="target")

    def test_missing_target_col_raises(self, sample_df):
        pre = DataPreprocessor()
        with pytest.raises(ValueError, match="not found"):
            pre.fit_transform(sample_df, target_col="nonexistent")

    def test_no_target_returns_none(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df)
        assert y is None


# ---------------------------------------------------------------------------
# DataPreprocessor — transform (no data leakage)
# ---------------------------------------------------------------------------

class TestTransform:
    def test_transform_not_fitted_raises(self, sample_df):
        pre = DataPreprocessor()
        with pytest.raises(RuntimeError, match="fitted"):
            pre.transform(sample_df)

    def test_transform_uses_training_medians(self, sample_df):
        """D-01: Training medians must be used — not inference-time medians."""
        pre = DataPreprocessor()
        X, _ = pre.fit_transform(sample_df, target_col="target")

        # Build inference row with nulls
        row = pd.DataFrame(
            [{"age": np.nan, "income": np.nan, "credit_score": np.nan,
              "employment_type": "Full-Time", "region": "North"}]
        )
        X_inf = pre.transform(row)
        assert not X_inf.isnull().any().any()

    def test_unseen_label_handled_gracefully(self, sample_df):
        """D-02: Unknown categories must not raise ValueError."""
        pre = DataPreprocessor()
        pre.fit_transform(sample_df, target_col="target")

        row = pd.DataFrame(
            [{"age": 30, "income": 50000.0, "credit_score": 650,
              "employment_type": "BRAND_NEW_CATEGORY", "region": "Mars"}]
        )
        X_inf = pre.transform(row)   # must not raise
        assert X_inf is not None

    def test_missing_feature_column_raises(self, sample_df):
        """D-09: Column consistency must be enforced."""
        pre = DataPreprocessor()
        pre.fit_transform(sample_df, target_col="target")

        bad_row = pd.DataFrame([{"age": 30}])  # missing most columns
        with pytest.raises(ValueError, match="Missing feature columns"):
            pre.transform(bad_row)


# ---------------------------------------------------------------------------
# DataPreprocessor — split
# ---------------------------------------------------------------------------

class TestSplit:
    def test_split_total_rows(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        X_train, X_val, X_test, y_train, y_val, y_test = pre.split(X, y)
        assert len(X_train) + len(X_val) + len(X_test) == len(X)

    def test_split_fractions_invalid(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        with pytest.raises(ValueError, match="must be < 1.0"):
            pre.split(X, y, test_size=0.6, val_size=0.5)

    def test_split_no_overlap(self, sample_df):
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        X_train, X_val, X_test, *_ = pre.split(X, y)
        train_idx = set(X_train.index)
        val_idx = set(X_val.index)
        test_idx = set(X_test.index)
        assert train_idx.isdisjoint(val_idx)
        assert train_idx.isdisjoint(test_idx)
        assert val_idx.isdisjoint(test_idx)


# ---------------------------------------------------------------------------
# DataPreprocessor — persistence
# ---------------------------------------------------------------------------

class TestPreprocessorPersistence:
    def test_save_load_roundtrip(self, tmp_path, sample_df):
        pre = DataPreprocessor()
        X_orig, _ = pre.fit_transform(sample_df, target_col="target")

        path = str(tmp_path / "preprocessor.joblib")
        pre.save(path)

        pre2 = DataPreprocessor.load(path)
        assert pre2.is_fitted

        # Transforms should be identical
        X_reloaded, _ = pre2.fit_transform(sample_df, target_col="target")
        # (fit_transform resets; test transform instead)
        row = sample_df.drop(columns=["target"]).iloc[:1]
        out1 = pre.transform(row)
        out2 = pre2.transform(row)
        pd.testing.assert_frame_equal(out1, out2)

    def test_save_unfitted_raises(self):
        pre = DataPreprocessor()
        with pytest.raises(RuntimeError, match="unfitted"):
            pre.save("/tmp/should_not_exist.joblib")

    def test_load_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            DataPreprocessor.load("/no/such/file.joblib")


# ---------------------------------------------------------------------------
# XGBoostModel
# ---------------------------------------------------------------------------

class TestXGBoostModel:
    def test_init_no_deprecated_param(self):
        """X-01: use_label_encoder must not be passed to XGBClassifier."""
        model = XGBoostModel(n_estimators=10)
        params = model.get_params()
        assert "use_label_encoder" not in params

    def test_random_state_set(self):
        """X-03: random_state must come from config."""
        model = XGBoostModel()
        assert model.get_params()["random_state"] is not None

    def test_train_predict(self, transformed_data):
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        model.train(X, y)
        preds = model.predict(X)
        assert len(preds) == len(X)
        assert set(preds).issubset({0, 1})

    def test_predict_proba_shape(self, transformed_data):
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        model.train(X, y)
        proba = model.predict_proba(X)
        assert proba.shape == (len(X), 2)
        assert np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)

    def test_evaluate_returns_all_metrics(self, transformed_data):
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        model.train(X, y)
        metrics = model.evaluate(X, y)
        for key in ("accuracy", "precision", "recall", "f1", "roc_auc"):
            assert key in metrics
            assert 0.0 <= metrics[key] <= 1.0

    def test_feature_importances_named(self, transformed_data):
        """X-07: Feature importances must return named dict, not raw array."""
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        model.train(X, y)
        fi = model.get_feature_importances()
        assert isinstance(fi, dict)
        assert len(fi) == X.shape[1]
        # Values should be sorted descending
        values = list(fi.values())
        assert values == sorted(values, reverse=True)

    def test_save_load_roundtrip(self, tmp_path, transformed_data):
        """X-02: Save/load must not crash; predictions must be identical."""
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        model.train(X, y)

        path = str(tmp_path / "model.joblib")
        model.save(path)

        # Native JSON should also be written
        import os
        json_path = path.replace(".joblib", ".json")
        assert os.path.exists(json_path)

        model2 = XGBoostModel()
        model2.load(path)
        np.testing.assert_array_equal(model.predict(X), model2.predict(X))

    def test_load_unsafe_extension_raises(self, tmp_path):
        """X-02: Loading a .exe file must be rejected."""
        bad = tmp_path / "model.exe"
        bad.write_text("malicious")
        model = XGBoostModel()
        with pytest.raises(ValueError, match="Unsafe"):
            model.load(str(bad))

    def test_load_nonexistent_raises(self):
        model = XGBoostModel()
        with pytest.raises(FileNotFoundError):
            model.load("/no/such/model.joblib")

    def test_early_stopping_with_val_set(self, transformed_data):
        """X-04: Training with a validation set must not crash."""
        pre, X, y = transformed_data
        X_train, X_val = X.iloc[:70], X.iloc[70:]
        y_train, y_val = y.iloc[:70], y.iloc[70:]
        model = XGBoostModel(n_estimators=50)
        model.train(X_train, y_train, X_val=X_val, y_val=y_val, early_stopping_rounds=10)
        assert model.predict(X_val) is not None

    def test_mismatched_val_raises(self, transformed_data):
        """X-04: Passing X_val without y_val must raise ValueError."""
        pre, X, y = transformed_data
        model = XGBoostModel(n_estimators=10)
        with pytest.raises(ValueError, match="both be provided"):
            model.train(X.iloc[:70], y.iloc[:70], X_val=X.iloc[70:])


# ---------------------------------------------------------------------------
# Integration: full pipeline smoke test
# ---------------------------------------------------------------------------

class TestEndToEndPipeline:
    def test_full_train_predict_pipeline(self, sample_df, tmp_path):
        """Smoke test: preprocess → train → evaluate → save → load → predict."""
        # Preprocess
        pre = DataPreprocessor()
        X, y = pre.fit_transform(sample_df, target_col="target")
        X_train, X_val, X_test, y_train, y_val, y_test = pre.split(X, y)

        # Train
        model = XGBoostModel(n_estimators=20)
        model.train(X_train, y_train, X_val=X_val, y_val=y_val)

        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        assert metrics["accuracy"] > 0.0

        # Save + reload
        model_path = str(tmp_path / "pipeline_model.joblib")
        pre_path = str(tmp_path / "pipeline_pre.joblib")
        model.save(model_path)
        pre.save(pre_path)

        model2 = XGBoostModel()
        model2.load(model_path)
        pre2 = DataPreprocessor.load(pre_path)

        # Inference on a single raw row
        raw_row = sample_df.drop(columns=["target"]).iloc[:1]
        X_inf = pre2.transform(raw_row)
        pred = model2.predict(X_inf)
        assert len(pred) == 1
        assert pred[0] in (0, 1)
