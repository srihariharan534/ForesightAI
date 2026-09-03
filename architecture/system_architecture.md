# ForesightAI — System Architecture

> **Version**: 1.0.0 | **Last Updated**: September 2026 | **Status**: Production

## Overview

ForesightAI is a cloud-native, microservices-inspired AI platform for loan risk prediction, Monte Carlo simulation, and explainable decision support. The system is built on a three-tier architecture: a React SPA frontend, a FastAPI backend, and a standalone ML Engine — all communicating via RESTful JSON APIs and integrated with MLflow for model lifecycle management.

---

## High-Level System Diagram

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI[React SPA<br/>Dashboard · Predict · Simulate · Risk Map]
    end

    subgraph Gateway["API Gateway / Reverse Proxy"]
        NGINX[NGINX<br/>SSL Termination · Rate Limiting · Load Balancing]
    end

    subgraph Backend["Backend Layer (FastAPI)"]
        API[API Router<br/>/api/v1/*]
        AUTH[Auth Middleware]
        CORS[CORS Middleware]
        METRICS[Prometheus Middleware]
    end

    subgraph Services["Service Layer"]
        PRED[PredictionService]
        DASH[DashboardService]
        RISK[RiskService]
        SIM[SimulationService]
    end

    subgraph ML["ML Engine"]
        PRE[DataPreprocessor]
        MODEL[XGBoostModel]
        SHAP[ModelExplainer / SHAP]
        MC[MonteCarloEngine]
        SCENARIO[ScenarioEngine]
    end

    subgraph Data["Data Layer"]
        DB[(SQLite / PostgreSQL<br/>Predictions · Users · KPIs · Risk Zones)]
        MLFLOW[(MLflow Registry<br/>Model Artifacts · Experiments)]
        DATASETS[Datasets<br/>raw · processed · sample]
    end

    subgraph Monitoring["Observability"]
        PROM[Prometheus]
        GRAF[Grafana Dashboard]
        LOGS[Structured Logging / Loguru]
        HEALTH[Health Checks<br/>Liveness · Readiness]
    end

    UI -->|HTTPS REST| NGINX
    NGINX --> API
    API --> AUTH --> CORS --> METRICS
    API --> PRED & DASH & RISK & SIM
    PRED --> PRE --> MODEL --> SHAP
    SIM --> MC & SCENARIO
    PRED & DASH & RISK --> DB
    MODEL --> MLFLOW
    METRICS --> PROM --> GRAF
    HEALTH --> PROM
    Backend --> LOGS
```

---

## Component Breakdown

| Component | Technology | Responsibility |
|---|---|---|
| **Frontend** | React 18, Recharts, Leaflet | Dashboard UI, prediction form, risk map |
| **API Gateway** | NGINX 1.25 | SSL, rate limiting, static asset serving |
| **Backend API** | FastAPI 0.103, Python 3.11 | REST endpoints, request validation, DB I/O |
| **ML Engine** | XGBoost 2.x, SHAP, scikit-learn | Training, inference, explainability |
| **Simulation** | NumPy, SciPy | Monte Carlo, scenario analysis, risk matrix |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Persistence for predictions, users, KPIs |
| **Model Registry** | MLflow 2.7 | Experiment tracking, model versioning |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualisation |

---

## Request Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as React Frontend
    participant NX as NGINX
    participant API as FastAPI
    participant SVC as Service Layer
    participant ML as ML Engine
    participant DB as Database
    participant MON as Prometheus

    User->>FE: Fill prediction form
    FE->>NX: POST /api/v1/predict/ (JSON)
    NX->>API: Forward request
    API->>API: Validate schema (Pydantic)
    API->>SVC: prediction_service.predict(data)
    SVC->>ML: preprocessor.transform(features)
    ML->>ML: model.predict_proba(X)
    ML->>ML: explainer.explain_instance(X)
    ML-->>SVC: {outcome, confidence, shap_values}
    SVC->>DB: INSERT prediction record
    DB-->>SVC: Saved record with ID
    SVC-->>API: PredictionResponse
    API->>MON: Record latency + outcome metrics
    API-->>NX: 200 JSON response
    NX-->>FE: Response
    FE->>User: Display result + SHAP chart
```

---

## Data Flow Architecture

```mermaid
flowchart LR
    RAW[Raw CSV Data] --> CLEAN[Data Cleaning<br/>02_Data_Cleaning.ipynb]
    CLEAN --> FEAT[Feature Engineering<br/>03_Feature_Engineering.ipynb]
    FEAT --> SPLIT{Train / Val / Test<br/>70/10/20}
    SPLIT --> TRAIN[Model Training<br/>trainer.py]
    TRAIN --> EVAL[Evaluation<br/>metrics.json]
    TRAIN --> MLFLOW[(MLflow Registry)]
    MLFLOW --> INFER[InferencePipeline]
    INFER --> API[FastAPI /predict]
    API --> DB[(Database)]
    API --> PROM[Prometheus Metrics]
```

---

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│                      ForesightAI Stack                      │
├─────────────┬───────────────────────────────────────────────┤
│ Layer       │ Technologies                                  │
├─────────────┼───────────────────────────────────────────────┤
│ Frontend    │ React 18 · Recharts · Leaflet · Axios        │
│ API         │ FastAPI · Uvicorn · Pydantic v2              │
│ ML          │ XGBoost · SHAP · scikit-learn · NumPy/SciPy  │
│ MLOps       │ MLflow · joblib · Optuna                     │
│ Database    │ SQLAlchemy · Alembic · SQLite/PostgreSQL      │
│ DevOps      │ Docker · docker-compose · GitHub Actions     │
│ Monitoring  │ Prometheus · Grafana · Loguru                │
│ Testing     │ pytest · httpx · pytest-cov                  │
│ Security    │ python-jose · passlib[bcrypt]                │
└─────────────┴───────────────────────────────────────────────┘
```

---

## Scalability Considerations

- **Horizontal scaling**: Backend stateless; can run N replicas behind NGINX upstream.
- **ML inference**: Model loaded once at startup; thread-safe for concurrent reads.
- **Database**: SQLite → PostgreSQL migration via Alembic with zero code changes.
- **Async support**: FastAPI async endpoints ready; DB calls can be migrated to `asyncpg`.
- **Caching**: Redis can be added for dashboard KPI caching (sub-10ms response).
- **Batch inference**: `InferencePipeline.predict_batch()` handles bulk scoring efficiently.

---

## Security Architecture

```mermaid
graph LR
    EXT[External Traffic] -->|HTTPS only| NGINX
    NGINX -->|Rate limit: 100 req/min| API
    API -->|JWT validation| AUTH_MW[Auth Middleware]
    AUTH_MW -->|Validated request| ROUTES[Route Handlers]
    ROUTES -->|Parameterised queries| DB
    DB -->|Encrypted at rest| STORAGE[(Storage)]
    ML_LOAD[Model Loading] -->|Path validation + extension allowlist| SAFE[Safe Deserialisation]
```

| Threat | Mitigation |
|---|---|
| SQL Injection | SQLAlchemy ORM parameterised queries |
| Pickle RCE | Extension allowlist + path validation on `joblib.load()` |
| Secret exposure | `.env` files excluded from git; env vars in deployment |
| Rate abuse | NGINX rate limiting + FastAPI middleware |
| Model poisoning | MLflow signed artifacts + input schema validation |
