# ForesightAI — Backend Architecture

> **Framework**: FastAPI 0.103 | **Language**: Python 3.11 | **ORM**: SQLAlchemy 2.x

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app factory, lifespan, middleware
│   ├── core/
│   │   ├── config.py              # Pydantic BaseSettings
│   │   └── database.py            # SQLAlchemy engine, session factory
│   ├── api/
│   │   └── api_v1/
│   │       ├── api.py             # APIRouter aggregator
│   │       └── endpoints/
│   │           ├── predict.py     # POST /predict/
│   │           ├── dashboard.py   # GET /dashboard/
│   │           ├── risk.py        # GET /risk/zones
│   │           ├── simulation.py  # POST /simulate/
│   │           └── users.py       # GET /users/
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── prediction.py          # Prediction table
│   │   ├── risk.py                # RiskZone table
│   │   ├── user.py                # User table
│   │   └── dashboard.py           # KPI, ActivityFeed, TrendData, RiskDistribution
│   ├── schemas/                   # Pydantic v2 request/response schemas
│   │   ├── prediction.py          # PredictionCreate, PredictionResponse
│   │   ├── risk.py                # RiskZoneItem
│   │   └── dashboard.py           # DashboardResponse
│   └── services/                  # Business logic layer
│       ├── prediction_service.py  # ML inference orchestration
│       └── dashboard_service.py   # KPI aggregation
```

---

## Layer Architecture

```mermaid
graph TB
    subgraph HTTP["HTTP Layer"]
        REQ[Incoming Request] --> CORS[CORS Middleware]
        CORS --> AUTH[Auth Middleware]
        AUTH --> METRICS[Prometheus Middleware]
        METRICS --> VALID[Pydantic Validation]
    end

    subgraph Route["Route Handlers (endpoints/)"]
        PREDICT[POST /predict/]
        DASH[GET /dashboard/]
        RISK[GET /risk/zones]
        SIM[POST /simulate/]
        USERS[GET /users/]
    end

    subgraph Service["Service Layer (services/)"]
        PRED_SVC[PredictionService]
        DASH_SVC[DashboardService]
    end

    subgraph ML["ML Engine"]
        PIPE[InferencePipeline]
        MC_ENG[MonteCarloEngine]
    end

    subgraph Data["Data Layer"]
        DB[(SQLAlchemy Session)]
    end

    VALID --> PREDICT & DASH & RISK & SIM & USERS
    PREDICT --> PRED_SVC
    DASH --> DASH_SVC
    PRED_SVC --> PIPE
    SIM --> MC_ENG
    PRED_SVC & DASH_SVC --> DB
    RISK & USERS --> DB
```

---

## API Router Configuration

```python
# api/api_v1/api.py
router = APIRouter()
router.include_router(predict.router,    prefix="/predict",   tags=["Prediction"])
router.include_router(dashboard.router,  prefix="/dashboard", tags=["Dashboard"])
router.include_router(risk.router,       prefix="/risk",      tags=["Risk"])
router.include_router(simulation.router, prefix="/simulate",  tags=["Simulation"])
router.include_router(users.router,      prefix="/users",     tags=["Users"])

# app/main.py
app.include_router(api_router, prefix="/api/v1")
```

---

## Database Schema

```mermaid
erDiagram
    PREDICTIONS {
        string id PK
        json input_features
        string predicted_outcome
        float confidence_score
        json shap_values
        datetime created_at
    }
    RISK_ZONES {
        string id PK
        string label
        float lat
        float lng
        int radius
        string risk
    }
    USERS {
        string id PK
        string name
        string email
        string role
        string status
    }
    KPI {
        string id PK
        int total_models
        int active_simulations
        float system_health
        int critical_alerts
        int predictions_last_24h
        float avg_confidence
    }
    ACTIVITY_FEED {
        string id PK
        string type
        string message
        string status
        datetime created_at
    }
    TREND_DATA {
        string id PK
        string name
        int predictions
        float accuracy
    }
    RISK_DISTRIBUTION {
        string id PK
        string name
        int value
        string color
    }
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| ORM | SQLAlchemy 2.x | Type-safe, async-ready, vendor-neutral |
| Validation | Pydantic v2 | 5–10x faster than v1; native `model_config` |
| DB (dev) | SQLite | Zero-config, file-based, test-friendly |
| DB (prod) | PostgreSQL | ACID, concurrent writes, JSON column support |
| Session injection | `Depends(get_db)` | Testable; cleanly overridden in tests |
| Async | Sync (uvicorn) | ML inference is CPU-bound; async adds no benefit here |
| CORS | `CORSMiddleware` | Allow `http://localhost:5173` in dev |

---

## Error Handling

All endpoints follow RFC 7807 Problem Details pattern:

```json
{
  "detail": "Prediction failed: Model not loaded.",
  "status": 500,
  "type": "InferenceError"
}
```

- 422 Unprocessable Entity: Pydantic validation failures (auto-generated)
- 500 Internal Server Error: Unhandled ML exceptions (caught in service layer)
- 404 Not Found: Resource lookup failures
