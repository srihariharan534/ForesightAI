# 10. Security & Privacy

## Introduction
ForesightAI handles sensitive business data and must be secured against threats.

## Purpose
To outline the security architecture and privacy controls.

## Detailed Explanation
- **Authentication**: Industry-standard JWT tokens with short expiration times and refresh token logic.
- **Password Hashing**: `bcrypt` via `passlib`.
- **Data Protection**: SQLAlchemy prevents SQL injection. FastAPI handles XSS and CSRF protections.
- **RBAC**: Endpoints are protected by dependency injection checking the user's role (Admin vs User).

## Diagrams
*(N/A)*

## Tables
| Threat | Mitigation |
|--------|------------|
| SQL Injection | SQLAlchemy ORM parameterized queries |
| XSS | React auto-escaping, FastAPI validation |
| Brute Force | Rate Limiting middleware |

## Examples
- Using `Depends(get_current_active_user)` in FastAPI to secure an endpoint.

## Best Practices
- Regularly audit dependencies for CVEs using `pip-audit` or Dependabot.
- Enforce HTTPS strictly in production.

## Future Improvements
- Integration with enterprise SSO (SAML/OAuth2).
- Data anonymization pipelines for training ML models on PII data.
