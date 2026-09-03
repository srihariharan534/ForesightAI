# ForesightAI — Decision Flow Architecture

> How ForesightAI makes and explains every loan risk decision.

---

## End-to-End Decision Flow

```mermaid
flowchart TD
    START([Loan Application Received]) --> VALIDATE{Input Validation}
    VALIDATE -->|Invalid| REJ_SCHEMA[Return 422 Validation Error]
    VALIDATE -->|Valid| PREPROCESS[DataPreprocessor.transform]

    PREPROCESS --> SCORE[XGBoostModel.predict_proba]
    SCORE --> CONF{Confidence >= 0.7?}
    CONF -->|Low| FLAG[Flag for Human Review]
    CONF -->|High| THRESHOLD{P-high-risk >= 0.50?}
    FLAG --> THRESHOLD

    THRESHOLD -->|Yes| HIGH_RISK[Predicted: HIGH RISK - Rejected]
    THRESHOLD -->|No| LOW_RISK[Predicted: LOW RISK - Approved]

    HIGH_RISK & LOW_RISK --> SHAP[SHAP TreeExplainer]
    SHAP --> RISK_MATRIX[RiskMatrix.evaluate]
    RISK_MATRIX --> STORE[Database INSERT - Full audit trail]
    STORE --> RESPONSE([Return PredictionResponse])
```

---

## Risk Classification Decision Tree

```mermaid
flowchart LR
    PD{P-default?} -->|less than 10%| LOW[LOW RISK - Score 1-4]
    PD -->|10-30%| MED[MEDIUM RISK - Score 5-9]
    PD -->|30-60%| HIGH[HIGH RISK - Score 10-16]
    PD -->|over 60%| CRIT[CRITICAL RISK - Score 17-25]

    LOW --> ACT1[Auto Approve]
    MED --> ACT2[Conditional Approval]
    HIGH --> ACT3[Manual Review]
    CRIT --> ACT4[Auto Reject]
```

---

## SHAP Contribution Verification

Each prediction satisfies the local accuracy axiom:

```
P(default) = base_value + sum(SHAP contributions)
0.2800     = 0.053      + 0.227
```

Top contributors for a high-risk applicant:
- `has_previous_default`: +0.412 (largest positive push toward risk)
- `credit_score`: +0.199
- `income`: -0.143 (protective)
- `loan_amount`: +0.092
- `years_employed`: -0.052 (protective)

---

## Bayesian Risk Lifecycle

After initial scoring, risk is continuously updated via `ProbabilityEngine`:

```mermaid
stateDiagram-v2
    [*] --> InitialScore : Loan approved, P = 0.08
    InitialScore --> Updated_1 : on_time_payment, P = 0.065
    Updated_1 --> Updated_2 : on_time_payment, P = 0.052
    Updated_2 --> Updated_3 : income_decrease, P = 0.091
    Updated_3 --> Updated_4 : missed_payment, P = 0.247
    Updated_4 --> Alert : P > 0.20, trigger alert
    Alert --> ManualReview : Loan officer review
    ManualReview --> Resolved : Restructured
    Resolved --> [*]
```

---

## Scenario-Based Approval Policy

| Worst-Case P(default) | Decision | Capital Action |
|---|---|---|
| < 20% | Auto Approve | Standard reserve |
| 20–40% | Conditional Approval | 15% additional reserve |
| > 40% | Decline | Offer reduced loan amount |

---

## Outcome Traceability

Every decision is stored in the `predictions` table with:

- Full input feature vector (JSON)
- Predicted class + confidence score
- SHAP contribution dictionary
- Timestamp + UUID

This enables complete regulatory audit trail per RBI guidelines on AI-assisted credit decisions.
