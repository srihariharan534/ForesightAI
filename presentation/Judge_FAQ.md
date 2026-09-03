# ForesightAI — Judge FAQ

> Prepared for the National AI Hackathon 2026 judging panel.

---

## Technical Questions

**Q: Why XGBoost instead of a deep learning model?**

> XGBoost is the gold standard for tabular credit data. It outperforms neural networks on datasets < 1M rows, is inherently interpretable via SHAP, requires 10x less compute, and is the most used model in production credit scoring (Kaggle lending competition winners, FICO, Experian). We optimised for accuracy-latency-explainability tradeoff, not model complexity.

**Q: How does the SHAP explainer work?**

> We use `TreeExplainer` (SHAP's most efficient algorithm for tree-based models). For each prediction, it decomposes the model output into additive feature contributions: `prediction = base_value + sum(SHAP values)`. This satisfies local accuracy, consistency, and missingness axioms — making it provably fair and RBI-compliant for loan decisions.

**Q: What is the Monte Carlo simulation doing?**

> For each loan application, we run 10,000 stochastic simulations by sampling uncertainty distributions around the input features (income ±20%, credit score ±5%, etc.). This produces the full P(default) distribution — not just a point estimate — giving us VaR at 95%/99%, confidence intervals, and Expected Shortfall. The Scenario Engine then applies 8 pre-defined economic shocks to stress-test every application.

**Q: How do you prevent data leakage?**

> Critical design decision: `DataPreprocessor.fit_transform()` computes imputation statistics (medians, label encodings) on training data only and stores them. `transform()` at inference time applies stored statistics — never recomputes from inference data. This is enforced by the `is_fitted` flag and raises `RuntimeError` if `transform()` is called on an unfitted preprocessor. Verified by `test_transform_uses_training_medians`.

**Q: Is the model reproducible?**

> Yes. Global seeds are set at three levels: `random.seed(42)`, `numpy.random.seed(42)`, and `random_state=42` in XGBoost. MLflow logs all hyperparameters, dataset hashes, and the random seed per run. All training artifacts are version-tagged and stored immutably in the model registry.

**Q: What is your test coverage?**

> 33 tests in `tests/test_ml_engine.py` + 55 tests in `tests/test_simulation.py` + full API integration tests. Coverage targets >90% for `ml_engine` and `simulation` packages. Tests verified passing: 33/33 `test_ml_engine.py` in the current build.

**Q: How does the Bayesian probability engine work?**

> `ProbabilityEngine` starts with the model's P(default) as a Bayesian prior. As real-world events arrive (payments, delinquencies, income changes), it applies Bayesian updates using calibrated likelihood ratios via the odds-ratio form: `posterior_odds = prior_odds × LR^weight`. This enables continuous, lifecycle-aware risk monitoring beyond initial scoring.

---

## Business Questions

**Q: Who are your target customers?**

> Primary: India's 1,500+ NBFCs (Non-Banking Financial Companies) that originate ₹28 lakh crore in loans annually but lack access to sophisticated ML-based risk systems. Secondary: Cooperative banks, digital lenders (fintechs), and microfinance institutions serving 450 million underbanked Indians.

**Q: How is this different from CIBIL?**

> CIBIL provides a bureau score — a single number from credit history. ForesightAI provides: (1) real-time ML scoring using 10+ features including non-traditional data, (2) SHAP explanations for every decision (CIBIL is a black box), (3) Monte Carlo simulation for forward-looking risk, and (4) geographic risk intelligence. We complement CIBIL rather than replace it.

**Q: What is the regulatory situation?**

> RBI's Guidelines on Responsible AI in Finance (2025) mandate explainability for automated credit decisions. SHAP explanations directly satisfy this requirement. Our audit trail (prediction stored with full feature set + SHAP values in PostgreSQL) enables regulatory review. DPDP Act compliance: all PII is handled via parameterised queries and no plaintext storage.

**Q: What is the revenue model?**

> SaaS subscription: ₹2,000–₹50,000/month based on prediction volume tiers. Enterprise: One-time license + annual maintenance. API marketplace: Pay-per-prediction at ₹2–₹15. Year 1 target: ₹48 lakh ARR from 50 NBFC pilots.

---

## Design Questions

**Q: Why a React dashboard instead of a mobile-first app?**

> Loan officers and risk analysts work on desktop in operations centres. The React dashboard is optimised for that workflow — multi-panel view with the risk map, trend charts, and prediction form simultaneously. A React Native mobile app for field officers is on the 6-month roadmap.

**Q: How is the frontend connected to the ML model?**

> The React frontend calls `POST /api/v1/predict/` with raw JSON features. The FastAPI backend invokes `prediction_service.predict()`, which calls `DataPreprocessor.transform()` then `XGBoostModel.predict_proba()` then `ModelExplainer.explain_instance()`. The full pipeline runs in 2.3ms average.
