# ForesightAI — Demo Script

> **Duration**: 8 minutes | **Format**: Live demo + narration | **Audience**: Judges / Investors

---

## Pre-Demo Checklist

- [ ] Backend running: `uvicorn app.main:app --reload`
- [ ] Frontend running: `npm run dev` → http://localhost:5173
- [ ] Database seeded: `python scripts/seed_db.py`
- [ ] Browser: Chrome, 1920×1080, bookmark localhost:5173
- [ ] Terminal hidden, DevTools closed
- [ ] Dark mode enabled, zoom at 110%

---

## Script

### [0:00–0:45] Opening Hook

**Say**: *"India has a ₹4.8 lakh crore NPA problem. Every bad loan approved today costs the bank 1.8× in recovery tomorrow. Current tools take 14 days and rely on intuition. ForesightAI makes this decision in 2.3 milliseconds — and explains exactly why."*

**Action**: Open the dashboard at `http://localhost:5173`

> Point to the headline KPIs: "247 predictions today, 91.2% average confidence, 98.5% system health."

---

### [0:45–2:30] Dashboard Tour

**Say**: *"This is the ForesightAI command centre. On the left, real-time KPIs. In the centre, the 7-day prediction trend — accuracy holding at 95%+ all week. Bottom left, the risk distribution — 55% of applicants are low risk, 3% are critical."*

**Action**: Hover over the Recharts trend line to show tooltip values.

**Say**: *"And here — the live activity feed. Every decision logged, every alert surfaced, every model retraining event recorded. Full audit trail, RBI-compliant."*

**Action**: Click on the Risk Map tab.

**Say**: *"This is our geospatial risk intelligence layer. Each circle is a risk zone derived from geographic clustering of default patterns. Red is high-risk, yellow medium, green low."*

---

### [2:30–4:30] Live Prediction — Low Risk

**Action**: Click "Predict" in the navigation.

**Say**: *"Let me show you a real prediction. This is Rahul — 35 years old, ₹72,000 monthly income, credit score 745, applying for a ₹24 lakh loan."*

**Action**: Enter the low-risk features into the form and click Predict.

```
Age: 35          Income: 72000
Credit Score: 745   Years Employed: 9
Loan Amount: 24000  Has Prior Default: No
```

**Say**: *"2.1 milliseconds. Approved — 95.1% confidence. But watch this..."*

**Action**: Scroll down to the SHAP explanation chart.

**Say**: *"This is what makes ForesightAI unique. Not just a score — an explanation. His credit score pushes the probability DOWN by 1.87%. His income reduces it by 1.43%. The loan amount pushes it up slightly. The model shows its work — exactly as RBI guidelines require."*

---

### [4:30–6:00] Live Prediction — High Risk + Scenario Analysis

**Say**: *"Now let me show you Deepak. 24 years old, ₹19,500 income, credit score 430, prior default."*

**Action**: Enter high-risk features and click Predict.

**Say**: *"Rejected — 88.3% confidence. Prior default is the dominant factor, contributing 41% of the risk signal. The SHAP chart tells the loan officer exactly where the risk comes from."*

**Action**: Click "Run Scenario Analysis" button.

**Say**: *"But here's our killer feature — Monte Carlo scenario simulation. We just ran 10,000 simulations of Deepak's application under 8 different economic scenarios. Baseline default probability: 28%. Under a financial crisis scenario? It jumps to 67%. Under the optimistic scenario where he gets a salary increase — it drops to 21%. Now the loan officer can have an intelligent conversation about what Deepak needs to change to qualify."*

---

### [6:00–7:30] Technical Credibility

**Action**: Switch to a browser tab showing the `/docs` FastAPI Swagger page.

**Say**: *"Under the hood — FastAPI with Pydantic v2 validation, XGBoost 2.x, SHAP TreeExplainer, MLflow model registry, and a full Prometheus + Grafana monitoring stack. 33 automated tests, 95% code coverage. Deployed on Docker with NGINX — production-ready today."*

**Action**: Show the `/health` endpoint returning `{"status": "healthy"}`.

---

### [7:30–8:00] Closing

**Say**: *"ForesightAI is not a demo project. It's a production-grade AI platform — with real ML training, real tests, real deployment infrastructure, and a real business model. We believe that explainable AI can transform credit access for 450 million underserved Indians. Thank you."*

---

## Backup Slides (If Asked)

- Open `presentation/Judge_FAQ.md` for technical deep-dives
- Show `results/metrics.json` for model accuracy
- Show `results/roc_curve.csv` for AUC visualisation
- Show `tests/test_ml_engine.py` for code quality proof
