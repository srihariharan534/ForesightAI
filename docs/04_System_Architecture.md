# 04. System Architecture

## Introduction
ForesightAI is built on a modern, decoupled microservice-ready architecture.

## Purpose
To document the structural design of the software, detailing the frontend, backend, database, and ML engine components.

## Detailed Explanation
- **Frontend**: React 19 SPA, bundled with Vite. State is managed via Redux Toolkit. Styled with Tailwind CSS.
- **Backend**: FastAPI providing async REST endpoints. Uses Pydantic for validation and SQLAlchemy for ORM.
- **AI Engine**: Python-based inference scripts decoupled from the web layer. Models are serialized and loaded into memory on startup. MLflow tracks artifacts.
- **Database**: PostgreSQL handles transactional data (users, history, recommendations). SQLite is used for local MLflow tracking.

## Diagrams
*(See `architecture/Component_Diagram.md` and `architecture/Deployment_Diagram.md`)*

## Tables
| Component | Stack | Responsibilities |
|-----------|-------|------------------|
| UI | React, Tailwind | Presentation, User Input |
| API | FastAPI, Uvicorn | Auth, Routing, Validation |
| DB | PostgreSQL, Alembic | Data Persistence |
| ML | XGBoost, MLflow | Inference, Training |

## Examples
- A request to `/api/v1/predict` passes through FastAPI middleware, hits the Inference Engine, logs to PostgreSQL, and returns JSON.

## Best Practices
- Use Dependency Injection in FastAPI to ensure the database and ML models are easily mockable during testing.
- Keep the ML Engine stateless for horizontal scaling.

## Future Improvements
- Migrate from REST to gRPC for internal microservice communication.
- Deploy via Kubernetes Helm charts.
