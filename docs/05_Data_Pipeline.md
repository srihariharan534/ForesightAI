# 05. Data Pipeline

## Introduction
The data pipeline is the backbone of ForesightAI, ensuring that raw data is transformed into high-quality features for the ML models.

## Purpose
To explain the ingestion, validation, cleaning, and engineering steps.

## Detailed Explanation
1. **Collection**: Data is ingested via CSV upload or API.
2. **Validation**: Pydantic schemas enforce strict type and range checks.
3. **Cleaning**: Missing values are imputed (e.g., median for numeric, mode for categorical). Outliers are capped.
4. **Feature Engineering**: Creation of rolling averages, interaction terms, and temporal features.
5. **Inference**: The cleaned feature vector is passed to the model.

## Diagrams
*(See `architecture/Data_Flow_Diagram.md`)*

## Tables
| Stage | Tooling | Output |
|-------|---------|--------|
| Validation | Pydantic | Validated dict |
| Cleaning | Pandas/NumPy | Clean DataFrame |
| Engineering | Scikit-Learn pipelines | Scaled Feature Array |

## Examples
- A raw date string `2026-09-01` is parsed and expanded into `day_of_week`, `is_weekend`, and `month` features.

## Best Practices
- Save the exact `StandardScaler` or `OneHotEncoder` artifacts used during training and apply them during inference to prevent data leakage.

## Future Improvements
- Implement Apache Airflow or Prefect for robust DAG-based data orchestration.
