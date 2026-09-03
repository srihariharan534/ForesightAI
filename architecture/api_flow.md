# ForesightAI — API Flow Architecture

> Complete request lifecycle diagrams for all API endpoints.

---

## POST /api/v1/predict/

```mermaid
sequenceDiagram
    actor Client
    participant NX as NGINX
    participant API as FastAPI
    participant SVC as PredictionService
    participant PRE as DataPreprocessor
    participant ML as XGBoostModel
    participant SHAP as ModelExplainer
    participant DB as Database
    participant PROM as Prometheus

    Client->>NX: POST /api/v1/predict/ {features}
    NX->>API: Rate-limited forward (20/min)
    API->>API: Pydantic validate PredictionCreate
    API->>SVC: prediction_service.predict(data, db)
    SVC->>PRE: preprocessor.transform(DataFrame)
    PRE-->>SVC: X (cleaned, encoded)
    SVC->>ML: model.predict(X) + predict_proba(X)
    ML-->>SVC: [class], [[p0, p1]]
    SVC->>SHAP: explainer.explain_instance(X)
    SHAP-->>SVC: {base_value, contributions}
    SVC->>DB: INSERT INTO predictions VALUES(...)
    DB-->>SVC: Saved Prediction ORM object
    SVC-->>API: PredictionResponse
    API->>PROM: track_prediction(outcome, latency)
    API-->>Client: 200 {id, predicted_outcome, confidence_score, shap_values, created_at}
```

**Happy path latency**: ~22ms (2.3ms inference + 18ms SHAP + 2ms DB write)

---

## GET /api/v1/dashboard/

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant SVC as DashboardService
    participant DB as Database

    Client->>API: GET /api/v1/dashboard/
    API->>SVC: dashboard_service.get_dashboard(db)
    SVC->>DB: SELECT * FROM kpi LIMIT 1
    DB-->>SVC: KPI row
    SVC->>DB: SELECT * FROM activity_feed ORDER BY created_at DESC LIMIT 10
    DB-->>SVC: Activity rows
    SVC->>DB: SELECT * FROM trend_data
    DB-->>SVC: Trend rows
    SVC->>DB: SELECT * FROM risk_distribution
    DB-->>SVC: Distribution rows
    SVC->>DB: SELECT * FROM risk_zones
    DB-->>SVC: Zone rows
    SVC-->>API: DashboardResponse (assembled)
    API-->>Client: 200 {kpis, activityFeed, trendData, riskDistribution, riskZones}
```

**Latency**: ~5ms (4 parallel-capable DB reads)  
**Optimisation path**: Redis cache with 60s TTL → sub-1ms

---

## POST /api/v1/simulate/

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant ENG as MonteCarloEngine
    participant SCN as ScenarioEngine

    Client->>API: POST /api/v1/simulate/ {params}
    API->>ENG: engine.run(params, n_simulations=5000)
    ENG->>ENG: Sample parameter distributions
    ENG->>ENG: Apply logistic risk model (vectorised)
    ENG-->>API: SimulationResult
    API->>SCN: scenario_engine.stress_test_summary(params)
    SCN->>SCN: Run 8 named scenarios
    SCN-->>API: {baseline_pd, scenarios, worst_case}
    API-->>Client: 200 {simulation, stress_test}
```

**Latency**: ~450ms for 5,000 simulations + 8 scenarios

---

## GET /api/v1/risk/zones

```mermaid
sequenceDiagram
    actor Client
    participant API as FastAPI
    participant DB as Database

    Client->>API: GET /api/v1/risk/zones
    API->>DB: SELECT id, label, lat, lng, radius, risk FROM risk_zones
    DB-->>API: [RiskZone, ...]
    API->>API: Transform: center=[lat, lng] format for Leaflet
    API-->>Client: 200 [{id, label, center, radius, risk}, ...]
```

---

## Health Check Endpoints

| Endpoint | Method | Purpose | Response |
|---|---|---|---|
| `/health` | GET | Liveness probe | `{"status": "healthy", "uptime_seconds": N}` |
| `/health/ready` | GET | Readiness probe | Full check report with per-component status |
| `/metrics` | GET | Prometheus scrape | Text format Prometheus metrics |
| `/docs` | GET | Swagger UI | Interactive API documentation |
| `/openapi.json` | GET | OpenAPI schema | Machine-readable schema |

---

## Error Response Format

All errors follow RFC 7807:

```json
{
  "detail": "Preprocessor not fitted. Call fit_transform() before transform().",
  "type": "RuntimeError",
  "status": 500
}
```

| HTTP Code | When | Example |
|---|---|---|
| 200 | Success | Prediction returned |
| 422 | Validation failure | Missing `features` key |
| 500 | Service error | Model not loaded |
| 429 | Rate limited | >20 predict requests/min |
