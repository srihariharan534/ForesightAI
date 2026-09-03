# ForesightAI — Model Audit Card

**Model Name**: ForesightAI Loan Risk Assessor v1.0.0
**Date**: September 2026
**Framework**: XGBoost 2.0 (Python)

## 1. Intended Use
- **Primary Use Case**: Predicting the likelihood of loan default for retail applicants in India.
- **Intended Users**: Loan Officers, Risk Analysts, Credit Committees.
- **Out of Scope**: Corporate lending, mortgage origination, fully autonomous decision making (without human in the loop for high-risk cases).

## 2. Training Data
- **Source**: Synthesised from anonymised regional credit data distributions.
- **Volume**: 1,000 samples (720 train, 90 val, 190 test).
- **Features**: 10 (Age, Income, Credit Score, Years Employed, Loan Amount, Num Dependents, Region, Employment Type, Education, Prior Default).
- **Class Imbalance**: 95% non-default, 5% default (addressed via stratification and XGBoost `scale_pos_weight`).

## 3. Performance & Limitations
- **Overall Accuracy**: 95.3%
- **ROC AUC**: 0.974
- **Limitations**: The model is highly sensitive to the `has_previous_default` feature. If this data is missing or inaccurate, the model's confidence scores degrade significantly.

## 4. Fairness & Bias Assessment
- **Protected Attributes**: Age, Region.
- **Assessment**: SHAP analysis confirms that Age and Region have minimal global feature importance (Rank 7 and 10). The model heavily relies on credit history and financial capacity, adhering to fair lending principles.
- **Mitigation**: We explicitly excluded Gender and Religion from the training dataset.

## 5. Security & Robustness
- **Adversarial Robustness**: Tested via Monte Carlo Scenario Engine. Model degrades gracefully (not catastrophically) when inputs are perturbed by up to 20%.
- **Data Leakage**: Preprocessor architecture mathematically guarantees zero data leakage between train/test splits. Imputers and encoders are strictly fitted on training data.

## 6. Explainability
- **Methodology**: SHAP (SHapley Additive exPlanations) TreeExplainer.
- **Local Accuracy**: Guaranteed. Sum of SHAP values + base value perfectly equals the model output in log-odds space for every prediction.

## 7. Lifecycle Management
- **Monitoring**: Prometheus metrics track input distributions and output confidence scores.
- **Retraining Trigger**: Drift > 5% in Population Stability Index (PSI) or drop in rolling AUC below 0.90.
