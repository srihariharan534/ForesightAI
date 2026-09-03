# 07. API Documentation

## Introduction
The backend exposes a secure REST API conforming to OpenAPI standards.

## Purpose
To outline the primary endpoints, authentication, and data structures.

## Detailed Explanation
- **Authentication**: JWT-based. Send `Authorization: Bearer <token>`.
- **Endpoints**:
  - `POST /api/v1/auth/login`: Retrieve JWT.
  - `POST /api/v1/predict`: Run single inference.
  - `POST /api/v1/predict/batch`: Run batch inference.
  - `GET /api/v1/history`: Retrieve past predictions (paginated).
  - `POST /api/v1/simulate`: Run what-if scenario.

## Diagrams
*(See `architecture/Sequence_Diagram.md`)*

## Tables
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/predict` | POST | Yes | Returns prediction & SHAP |
| `/history` | GET | Yes | Fetches user's history |
| `/health` | GET | No | Liveness probe |

## Examples
**Request:**
```json
{
  "features": { "age": 30, "income": 50000 }
}
```
**Response:**
```json
{
  "prediction": "Approved",
  "confidence": 0.92,
  "recommendation": "Proceed with standard processing."
}
```

## Best Practices
- Always use the Swagger UI (`/docs`) to test endpoints during development.
- Ensure all inputs are validated via Pydantic schemas.

## Future Improvements
- GraphQL support for dynamic frontend querying.
- WebSocket endpoints for real-time model training progress.
