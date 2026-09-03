"""Generate a realistic synthetic dataset for ForesightAI demos and tests.

This script creates a CSV file at datasets/sample/sample_data.csv with
1000 rows of plausible risk-prediction features and a binary target.

Usage::

    python scripts/generate_sample_data.py
    python scripts/generate_sample_data.py --rows 5000 --output datasets/sample/large.csv
"""

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd


def generate(n_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic risk-prediction dataset.

    Args:
        n_rows: Number of rows to generate.
        seed: Random seed for reproducibility.

    Returns:
        A DataFrame with realistic features and a binary target column.
    """
    rng = np.random.default_rng(seed)
    random.seed(seed)

    age = rng.integers(18, 75, n_rows)
    income = rng.normal(55_000, 18_000, n_rows).clip(10_000, 200_000).round(2)
    credit_score = rng.integers(300, 850, n_rows)
    years_employed = rng.integers(0, 40, n_rows)
    loan_amount = rng.normal(25_000, 12_000, n_rows).clip(1_000, 100_000).round(2)
    num_dependents = rng.integers(0, 6, n_rows)
    region = rng.choice(["North", "South", "East", "West", "Central"], n_rows)
    employment_type = rng.choice(
        ["Full-Time", "Part-Time", "Self-Employed", "Unemployed"], n_rows,
        p=[0.55, 0.20, 0.15, 0.10]
    )
    education = rng.choice(
        ["High School", "Bachelor", "Master", "PhD", "None"], n_rows,
        p=[0.30, 0.40, 0.20, 0.05, 0.05]
    )
    has_previous_default = rng.choice([0, 1], n_rows, p=[0.82, 0.18])

    # Simulate a realistic (non-trivial) binary target
    # Higher credit score, income, employment → lower risk
    log_odds = (
        -3.0
        + 0.03 * (credit_score - 600) / 100
        + 0.02 * (income - 55_000) / 10_000
        - 0.04 * (loan_amount / income)
        + 0.01 * years_employed
        - 1.2 * has_previous_default
        + rng.normal(0, 0.3, n_rows)   # noise
    )
    prob_high_risk = 1 / (1 + np.exp(-log_odds))
    target = (rng.random(n_rows) < prob_high_risk).astype(int)

    df = pd.DataFrame(
        {
            "age": age,
            "income": income,
            "credit_score": credit_score,
            "years_employed": years_employed,
            "loan_amount": loan_amount,
            "num_dependents": num_dependents,
            "region": region,
            "employment_type": employment_type,
            "education": education,
            "has_previous_default": has_previous_default,
            "target": target,
        }
    )

    # Introduce realistic missing values (~2% per numeric column)
    for col in ["income", "credit_score", "years_employed"]:
        mask = rng.random(n_rows) < 0.02
        df.loc[mask, col] = np.nan

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate ForesightAI synthetic sample data."
    )
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument(
        "--output",
        default="datasets/sample/sample_data.csv",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate(n_rows=args.rows, seed=args.seed)
    df.to_csv(output_path, index=False)

    print(f"[OK] Generated {len(df)} rows -> '{output_path}'")
    print(f"   Target distribution:\n{df['target'].value_counts().to_string()}")
    print(f"   Missing values:\n{df.isnull().sum().to_string()}")


if __name__ == "__main__":
    main()
