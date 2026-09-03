# ForesightAI — Pitch Deck

> **National AI Hackathon 2026** | Team ForesightAI | Category: FinTech / AI

---

## Slide 1 — Title

# ForesightAI
### Explainable AI for Smarter Loan Risk Assessment

> *"Predict the future. Protect the present."*

**Team**: ForesightAI  
**Track**: Enterprise AI / FinTech Innovation  
**Date**: September 2026

---

## Slide 2 — The Problem

### The ₹4.8 Lakh Crore NPA Crisis

India's banking system carries **₹4.8 lakh crore in Non-Performing Assets** as of 2026.

- **85% of bad loans** were approved using manual, intuition-based credit assessment
- **Average loan officer** processes 40 applications/day with 3 data points
- **Rejection bias**: 42% of creditworthy applicants rejected due to thin credit files
- **Time cost**: Traditional credit assessment takes 7–14 days per application

> Every ₹1 crore in bad loan costs the bank ₹1.8 crore in recovery, legal, and opportunity cost.

---

## Slide 3 — Our Solution

### ForesightAI: End-to-End AI Credit Risk Platform

```
Raw Application Data
        ↓
   AI Preprocessing (DataPreprocessor)
        ↓
XGBoost Risk Model (97.43% AUC)
        ↓
SHAP Explainability Engine
        ↓
Monte Carlo Scenario Analysis
        ↓
Risk-Adjusted Decision + Audit Trail
```

**Decision time**: 2.3ms average | **Accuracy**: 95.3% | **AUC**: 0.974

---

## Slide 4 — Product Demo

### Three Core Capabilities

| Capability | What It Does | Business Value |
|---|---|---|
| **AI Predict** | XGBoost scores loan risk with confidence | 95.3% accuracy, 2.3ms latency |
| **Explainability** | SHAP shows why each decision was made | Regulatory compliance (RBI guidelines) |
| **Scenario Engine** | Monte Carlo stress tests across 8 scenarios | Risk quantification before approval |
| **Risk Map** | Geospatial risk zone visualisation | Portfolio concentration management |
| **Live Dashboard** | Real-time KPIs, trends, activity feed | Operational visibility |

---

## Slide 5 — Technology

### Enterprise-Grade ML Stack

```
┌──────────────────────────────────────────┐
│  React 18 Dashboard  │  Leaflet Risk Map │
├──────────────────────────────────────────┤
│   FastAPI REST API   │   Prometheus +    │
│   (2.3ms latency)    │   Grafana         │
├──────────────────────────────────────────┤
│  XGBoost Classifier  │  SHAP Explainer   │
│  AUC: 0.974          │  TreeExplainer    │
├──────────────────────────────────────────┤
│  Monte Carlo Engine  │  Bayesian Updater │
│  10,000 simulations  │  Sequential PD    │
├──────────────────────────────────────────┤
│  MLflow Model Registry │ Docker + K8s   │
└──────────────────────────────────────────┘
```

---

## Slide 6 — AI Quality Results

### Model Performance (190-sample test set)

| Metric | Value | Industry Benchmark |
|---|---|---|
| Accuracy | **95.26%** | ~88% |
| ROC AUC | **0.9743** | ~0.85 |
| F1 Score | **0.857** | ~0.75 |
| Precision | **81.8%** | ~70% |
| Recall | **90.0%** | ~75% |
| Inference Latency | **2.3ms** | ~50ms |

> Our model outperforms the industry benchmark on every metric.

---

## Slide 7 — Market Opportunity

### Total Addressable Market

| Segment | Size | Growth |
|---|---|---|
| India Credit Risk Software | ₹12,400 Cr (2026) | 28% CAGR |
| BFSI AI Platform Market | ₹48,200 Cr (2030) | 34% CAGR |
| Global Credit Analytics | $32.4B (2028) | 22% CAGR |

**Target customers**: NBFCs, Cooperative Banks, Microfinance Institutions, Digital Lenders

**Beachhead**: 1,500+ NBFCs in India | ₹28 lakh crore AUM | 450M underserved borrowers

---

## Slide 8 — Business Model

### Three Revenue Streams

1. **SaaS Subscription** — ₹2,000–₹50,000/month per institution (based on API calls)
2. **Prediction API** — ₹2–₹15 per prediction (pay-per-use)
3. **Enterprise License** — One-time + annual maintenance for on-premise deployment

**Year 1 Target**: 50 NBFC clients × ₹8,000/month avg = ₹48 lakh ARR  
**Year 3 Target**: 500 clients + API revenue = ₹8.4 crore ARR

---

## Slide 9 — Competitive Advantage

| Feature | ForesightAI | CIBIL | Experian | Bureau Solutions |
|---|---|---|---|---|
| Explainable AI (SHAP) | ✅ | ❌ | ❌ | ❌ |
| Monte Carlo Simulation | ✅ | ❌ | ❌ | ❌ |
| Real-time inference (<10ms) | ✅ | ❌ | Partial | ❌ |
| Open source ML stack | ✅ | ❌ | ❌ | ❌ |
| On-premise deployment | ✅ | ❌ | ❌ | Partial |
| Thin-file borrower scoring | ✅ | ❌ | ❌ | Partial |
| Monthly SaaS pricing | ✅ | ❌ | ❌ | ❌ |

---

## Slide 10 — Traction & Roadmap

### Current Status
- ✅ MVP: All 5 modules built, tested, deployed
- ✅ 33 automated tests, 95%+ code coverage
- ✅ Real ML model trained on ForesightAI dataset (AUC 0.974)
- ✅ Live demo running on Render

### 6-Month Roadmap
```
Month 1–2: Pilot with 3 NBFCs → real data validation
Month 3–4: RBI-compliant audit trail + report generation
Month 5–6: Mobile app for field officers + API marketplace launch
```

---

## Slide 11 — The Ask

### We are seeking:

> **₹50 Lakh seed funding** to:
> - Hire 2 ML engineers + 1 sales lead
> - Pilot with 10 NBFCs (6-month free trial + data partnership)
> - Obtain CERT-IN security certification
> - File patent for SHAP+Monte Carlo risk fusion methodology

**Use of funds**: 40% engineering · 30% sales & marketing · 20% compliance · 10% operations

---

## Slide 12 — Team

| Name | Role | Background |
|---|---|---|
| **[Team Lead]** | ML Architect + Backend | IIT Delhi · 3 years ML engineering |
| **[Team Member 2]** | Frontend + UI/UX | NIT Trichy · React specialist |
| **[Team Member 3]** | MLOps + DevOps | AWS certified · 2 years cloud infra |

*"We built ForesightAI in 48 hours. Imagine what we can do with 6 months."*

---

## Contact

📧 team@foresightai.com  
🌐 https://foresightai.example.com  
💻 https://github.com/foresightai/foresightai
