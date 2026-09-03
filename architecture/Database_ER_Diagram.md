# Database Entity-Relationship Diagram

## Purpose
To map the relational schema used by SQLAlchemy for ForesightAI.

## Components
- **Users**: Authentication and profile data.
- **Predictions**: Stores historical inference requests and results.
- **Recommendations**: 1-to-N relationship with predictions.
- **Models**: Tracks deployed model metadata.

## Data Flow
- N/A

## Design Decisions
- Using UUIDs for primary keys to enhance security and prevent enumeration attacks.
- Foreign keys enforce data integrity between predictions and recommendations.

## Scalability Notes
- Indexes will be placed on `created_at` and `user_id` in the `Predictions` table to ensure fast history querying.

## Mermaid Diagram
```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string hashed_password
        string role
        datetime created_at
    }
    MODELS {
        uuid id PK
        string version
        string algorithm
        float accuracy_score
        datetime deployed_at
    }
    PREDICTIONS {
        uuid id PK
        uuid user_id FK
        uuid model_id FK
        jsonb input_features
        string predicted_outcome
        float confidence_score
        datetime created_at
    }
    RECOMMENDATIONS {
        uuid id PK
        uuid prediction_id FK
        string action_text
        string priority
        string impact
    }

    USERS ||--o{ PREDICTIONS : creates
    MODELS ||--o{ PREDICTIONS : powers
    PREDICTIONS ||--o{ RECOMMENDATIONS : generates
```
