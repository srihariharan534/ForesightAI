# ForesightAI — Dataset Architecture

Welcome to the `datasets/` directory of the ForesightAI platform. This directory acts as the central data lake and feature store for all ML models, simulation engines, and frontend demos.

## 📂 Folder Structure

```
datasets/
├── raw/         # Immutable, raw data ingested directly from sources
├── cleaned/     # Deduplicated, normalized data with imputed missing values
├── processed/   # ML-ready data (scaled, encoded, split into train/val/test)
├── sample/      # Small, curated slices (max 20 rows) for UI and testing
├── external/    # Documentation and references to third-party data sources
└── metadata/    # Schemas, dictionaries, versioning, and quality reports
```

## 🔄 Data Pipeline

The ForesightAI data engineering pipeline follows a strict, one-way ETL flow to guarantee reproducibility and prevent data leakage:

1. **Ingestion**: Raw CSVs from telemetry, APIs, and sensors are deposited into `raw/`. These are treated as append-only and immutable.
2. **Cleaning**: Automated scripts (`generate_all_datasets.py` in dev, or Airflow in prod) apply standard cleaning rules (median imputation, deduplication). The outputs are written to `cleaned/`, accompanied by a `cleaning_log.md`.
3. **Processing**: The ML engine reads from `cleaned/`, applies feature engineering, target extraction, and normalisation. Critically, fit statistics (like scaler means/stds) are calculated *only* on the training split to prevent leakage. Outputs are saved to `processed/`.

## ⚙️ Preprocessing Flow
- **Numerical Features**: Standardised using Z-score normalisation ($ \frac{x - \mu}{\sigma} $). Means and standard deviations are stored in `metadata/scaler_metadata.json`.
- **Categorical Features**: Label encoded for XGBoost compatibility. Mappings are stored in `metadata/feature_mapping.json`.

## 🏷️ Versioning Strategy
- We follow semantic versioning for datasets (e.g., `v1.0.0`).
- The active version and last-updated timestamp are tracked in `metadata/version.json`.
- In production, Data Version Control (DVC) is layered on top of this directory to version the `.csv` files alongside git commits.

## 🚀 Update Process
1. Drop new data into `raw/`.
2. Run `python scripts/generate_all_datasets.py` to regenerate the downstream artifacts.
3. Review `metadata/quality_report.md`.
4. Trigger the ML pipeline retraining.

## ⚖️ Licensing
- Synthetic and derived data generated for ForesightAI is released under the MIT License.
- External data referenced in `external/` remains under the respective licenses of their providers (e.g., Open Data Commons, NASA data policies).

## 🔒 Privacy Considerations
All datasets in this repository are strictly anonymised.
- Personal Identifiable Information (PII) such as caller names or phone numbers are stripped before ingestion into `raw/`.
- Geographic coordinates (`lat`, `lng`) in the emergency calls dataset are jittered by a random factor to protect exact residential locations.

## ✅ Data Quality Checks
Every pipeline run generates a `quality_report.md` evaluating:
- **Completeness**: Missing value tracking.
- **Uniqueness**: Duplicate row detection.
- **Validity**: Range and type assertions against `schema.json`.
- **Consistency**: Format normalization (e.g., ISO-8601 timestamps).
