"""CLI Inference Script for ForesightAI.

Run single-sample or batch inference using trained model and preprocessor artifacts.

Usage:
    # Run batch inference on a CSV file:
    python scripts/inference.py --data-path datasets/sample/sample_data.csv

    # Run single inference via JSON:
    python scripts/inference.py --json '{"age": 35, "income": 65000, "credit_score": 720, "years_employed": 8, "loan_amount": 22000, "num_dependents": 2, "region": "North", "employment_type": "Full-Time", "education": "Bachelor", "has_previous_default": 0}'

    # Include SHAP explainability:
    python scripts/inference.py --data-path datasets/sample/sample_data.csv --explain --limit 5
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

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
    parser = argparse.ArgumentParser(description="ForesightAI Inference Runner")
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path to trained XGBoost model (.joblib). Defaults to latest in models/artifacts.",
    )
    parser.add_argument(
        "--preprocessor-path",
        type=str,
        default=None,
        help="Path to fitted DataPreprocessor (.joblib). Defaults to latest in models/artifacts.",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="Path to input CSV file for batch inference.",
    )
    parser.add_argument(
        "--json",
        dest="json_str",
        type=str,
        default=None,
        help="Single sample features as a JSON string.",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default=None,
        help="Optional path to write predictions CSV/JSON.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum rows to display in terminal summary for batch mode (default: 10).",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Enable SHAP explainability for predictions.",
    )

    args = parser.parse_args()

    # Determine artifact paths
    model_path = args.model_path
    preprocessor_path = args.preprocessor_path

    if not model_path or not preprocessor_path:
        latest_model, latest_prep = find_latest_artifacts()
        model_path = model_path or latest_model
        preprocessor_path = preprocessor_path or latest_prep

    print(f"[+] Loading model: {model_path}")
    print(f"[+] Loading preprocessor: {preprocessor_path}")

    pipeline = InferencePipeline(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        enable_explanations=args.explain,
    )

    # 1. Single sample JSON inference
    if args.json_str:
        try:
            features = json.loads(args.json_str)
        except json.JSONDecodeError as err:
            print(f"[!] Invalid JSON: {err}")
            sys.exit(1)

        result = pipeline.predict_single(features, explain=args.explain)
        print("\n--- Single Prediction Result ---")
        print(f"Predicted Class : {result['predicted_class']}")
        print(f"Confidence Score: {result['confidence_score']:.4f}")
        print(f"Probabilities   : {result['probabilities']}")
        if result.get("shap_explanation"):
            print(f"SHAP Explanation: {json.dumps(result['shap_explanation'], indent=2)}")

        if args.output_path:
            with open(args.output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"\n[+] Saved result to {args.output_path}")
        return

    # 2. Batch CSV inference
    data_path = args.data_path or "datasets/sample/sample_data.csv"
    if not os.path.exists(data_path):
        print(f"[!] Input data file '{data_path}' not found.")
        sys.exit(1)

    print(f"[+] Loading input data from: {data_path}")
    df = pd.read_csv(data_path)

    # If target column is present, exclude it from feature input
    features_df = df.drop(columns=["target"]) if "target" in df.columns else df
    records = features_df.to_dict(orient="records")

    print(f"[+] Running batch inference on {len(records)} records...")
    results = pipeline.predict_batch(records, explain=args.explain)

    # Attach prediction outputs to DataFrame
    pred_df = features_df.copy()
    pred_df["predicted_class"] = [r["predicted_class"] for r in results]
    pred_df["confidence_score"] = [round(r["confidence_score"], 4) for r in results]
    if "target" in df.columns:
        pred_df["actual_target"] = df["target"].values

    print("\n--- Batch Prediction Summary (First Rows) ---")
    display_cols = [c for c in pred_df.columns if c not in ["shap_explanation"]][:8] + ["predicted_class", "confidence_score"]
    if "actual_target" in pred_df.columns:
        display_cols.append("actual_target")
    # De-duplicate display columns while preserving order
    display_cols = list(dict.fromkeys(display_cols))
    print(pred_df[display_cols].head(args.limit).to_string(index=False))

    class_counts = pred_df["predicted_class"].value_counts().to_dict()
    print("\n--- Class Distribution ---")
    for cls, count in sorted(class_counts.items()):
        print(f"Class {cls}: {count} ({count/len(pred_df)*100:.1f}%)")

    if args.output_path:
        pred_df.to_csv(args.output_path, index=False)
        print(f"\n[+] Saved batch predictions to {args.output_path}")


if __name__ == "__main__":
    main()
