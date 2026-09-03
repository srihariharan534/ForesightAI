# Sequence Diagram: Run Prediction

## Purpose
To document the step-by-step lifecycle of a prediction request from the frontend to the backend and back.

## Components
- Frontend, Backend (API), Prediction Service, AI Engine, Database.

## Data Flow
1. Client POSTs data.
2. Backend validates token and payload.
3. Backend passes data to Prediction Service.
4. Prediction Service calls AI Engine for inference and SHAP values.
5. Results are persisted to Database.
6. Backend returns JSON to Client.

## Design Decisions
- synchronous REST flow is used for real-time predictions. Batch predictions will use asynchronous background tasks (Celery/FastAPI Tasks).

## Scalability Notes
- Heavy SHAP computations can bottleneck the API. In future iterations, long-running predictions will return a `202 Accepted` and be polled via WebSocket.

## Mermaid Diagram
```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend
    participant API as FastAPI Router
    participant Svc as Prediction Service
    participant AI as AI Engine
    participant DB as PostgreSQL

    User->>UI: Submit Data Form
    UI->>API: POST /api/v1/predict (JWT)
    API->>API: Validate Token & Payload
    API->>Svc: Process Prediction
    Svc->>AI: generate_prediction(features)
    AI-->>Svc: confidence_score, outcome
    Svc->>AI: generate_explanation(features)
    AI-->>Svc: SHAP_values
    Svc->>DB: save_prediction_history()
    DB-->>Svc: record_id
    Svc-->>API: formatted_response
    API-->>UI: 200 OK (JSON)
    UI-->>User: Display Results Panel
```
