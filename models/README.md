# ForesightAI Model Repository

This directory serves as the local artifact repository for trained machine learning models, preprocessors (scalers and encoders), and their associated metadata.

## Directory Structure

```
models/
├── artifacts/
│   └── v1.0.0/
│       ├── xgboost_model.bin      # Trained XGBoost classifier
│       └── preprocessor.joblib    # Fitted scikit-learn pipeline (imputers, scalers, encoders)
├── README.md                      # This documentation
├── metadata.json                  # High-level model version and architecture details
├── model_metrics.json             # Evaluation metrics for the active model
└── feature_columns.json           # Ordered list of features expected by the model
```

## Important Note on Code vs. Artifacts
**No Python implementation code lives here.** 
- The classes that define the model architecture (e.g., `XGBoostModel`) are located in `ml_engine/models/`.
- The classes that define preprocessing (e.g., `DataPreprocessor`) are located in `ml_engine/data/`.
- This `models/` directory is strictly for **serialized binary artifacts** (`.bin`, `.joblib`, `.pkl`) and **configuration/metadata** (`.json`, `.yaml`).

## Deployment & MLOps Integration
In a production environment, this directory acts as a local cache for models pulled from the MLflow registry. 
The `InferencePipeline` (in `ml_engine/inference/pipeline.py`) expects to load its required assets from this structure.

### Updating the Model
When a new model is trained and vetted:
1. Serialize the new model and preprocessor to `models/artifacts/vX.Y.Z/`.
2. Update `metadata.json` with the new version and timestamp.
3. Update `model_metrics.json` with the new evaluation results.
4. Ensure `feature_columns.json` accurately reflects the new feature expectations if schema changes occurred.
