"""CLI Model Evaluation Script for ForesightAI.

Loads the latest trained model & preprocessor, evaluates on a dataset,
and prints full classification metrics (Accuracy, Precision, Recall, F1, ROC-AUC)
plus a confusion matrix.

Usage:
    python scripts/evaluate.py
    python scripts/evaluate.py --data-path datasets/sample/sample_data.csv --target-col target
"""

import argparse
import glob
import os
import sys
from typing import Tuple

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_engine.inference.pipeline import InferencePipeline


def find_latest_artifacts(artifacts_dir: str = "models/artifacts") -> Tuple[str, str]:
    """Find the latest model and preprocessor artifacts in the directory."""
    model_files = sorted(
        glob.glob(os.path.join(artifacts_dir, "xgboost_*.joblib")),
        key=os.path.getmtime,
        reverse=True,
    )
    preprocessor_files = sorted(
        glob.glob(os.path.join(artifacts_dir, "preprocessor_*.joblib")),
        key=os.path.getmtime,
        reverse=True,
    )

    if not model_files:
        raise FileNotFoundError(
            f"No trained model artifact (*.joblib) found in '{artifacts_dir}'. "
            f"Run training first: python -m ml_engine.training.trainer --data-path datasets/sample/sample_data.csv --target-col target"
        )
    if not preprocessor_files:
        raise FileNotFoundError(
            f"No preprocessor artifact (*.joblib) found in '{artifacts_dir}'."
        )

    return model_files[0], preprocessor_files[0]


def main():
    parser = argparse.ArgumentParser(description="ForesightAI Model Evaluator")
    parser.add_argument(
        "--data-path",
        type=str,
        default="datasets/sample/sample_data.csv",
        help="Path to labeled evaluation dataset CSV.",
    )
    parser.add_argument(
        "--target-col",
        type=str,
        default="target",
        help="Name of the true label / target column in the dataset.",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Optional path to model .joblib file.",
    )
    parser.add_argument(
        "--preprocessor-path",
        type=str,
        default=None,
        help="Optional path to preprocessor .joblib file.",
    )

    args = parser.parse_args()

    model_path = args.model_path
    preprocessor_path = args.preprocessor_path
    if not model_path or not preprocessor_path:
        latest_model, latest_prep = find_latest_artifacts()
        model_path = model_path or latest_model
        preprocessor_path = preprocessor_path or latest_prep

    print(f"[+] Loading model: {model_path}")
    print(f"[+] Loading preprocessor: {preprocessor_path}")
    print(f"[+] Loading dataset: {args.data_path}")

    if not os.path.exists(args.data_path):
        print(f"[!] Dataset '{args.data_path}' not found.")
        sys.exit(1)

    df = pd.read_csv(args.data_path)
    if args.target_col not in df.columns:
        print(f"[!] Target column '{args.target_col}' not found in dataset. Columns: {list(df.columns)}")
        sys.exit(1)

    y_true = df[args.target_col].values
    X_df = df.drop(columns=[args.target_col])

    pipeline = InferencePipeline(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        enable_explanations=False,
    )

    records = X_df.to_dict(orient="records")
    print(f"[+] Running evaluation across {len(records)} samples...")
    results = pipeline.predict_batch(records, explain=False)

    y_pred = [r["predicted_class"] for r in results]
    # For binary classification, probability of positive class
    y_prob = [r["probabilities"][1] if len(r["probabilities"]) > 1 else r["probabilities"][0] for r in results]

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        roc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc = float("nan")

    cm = confusion_matrix(y_true, y_pred)

    print("\n" + "=" * 45)
    print("        FORESIGHTAI EVALUATION REPORT")
    print("=" * 45)
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc:.4f}")
    print("-" * 45)
    print("Confusion Matrix:")
    print(cm)
    print("-" * 45)
    print("Classification Report:")
    print(classification_report(y_true, y_pred, zero_division=0))
    print("=" * 45)


if __name__ == "__main__":
    main()
