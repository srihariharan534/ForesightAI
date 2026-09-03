# 06. AI Model Explanation

## Introduction
ForesightAI relies on robust, transparent machine learning models.

## Purpose
To document the model selection, training, and explainability strategies.

## Detailed Explanation
- **Model Selection**: We default to tree-based ensembles (Random Forest, XGBoost) due to their high performance on tabular data and native support for SHAP tree explainers.
- **Training**: Managed via MLflow. Hyperparameters are tuned using Optuna (Bayesian Optimization).
- **Explainability**: SHAP (SHapley Additive exPlanations) is used to calculate the marginal contribution of each feature to the final prediction.
- **Confidence Scoring**: Probability outputs from `.predict_proba()` are mapped to a confidence risk matrix.

## Diagrams
*(See `architecture/ML_Pipeline.md`)*

## Tables
| Algorithm | Use Case | Explainability |
|-----------|----------|----------------|
| XGBoost | Primary Classifier | High (TreeSHAP) |
| LightGBM | Large Datasets | High (TreeSHAP) |
| Logistic Reg | Baseline | Very High (Coefficients) |

## Examples
- The model predicts "High Risk" with 85% probability. The SHAP summary shows that `Debt_to_Income_Ratio > 40` was the primary driver.

## Best Practices
- Always maintain a baseline model to prove the complex ensemble is actually adding value.
- Log SHAP values to the database to monitor feature drift over time.

## Future Improvements
- Implement continuous retraining pipelines triggered by data drift alerts.
