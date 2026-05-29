# Backend

## Technology Stack

- FastAPI
- SQLAlchemy 2.0 (async)
- asyncpg
- Pydantic v2
- PostgreSQL

## Project Structure

```text
app/
  api/
    v1/
      endpoints/
      router.py
  core/
    config.py
    database.py
  models/
  repositories/
  schemas/
  services/
  main.py
```

## Application Bootstrap

Entry point: `app/main.py`

What happens on startup:

- FastAPI app is initialized
- CORS middleware is enabled for local frontend origins
- API router is mounted under `/api/v1`
- Database schema is expected to be managed via Alembic migrations (`alembic upgrade head`)
- Health endpoint is exposed at `/health`
- If `frontend/dist` exists, SPA files are served by FastAPI

## Configuration

Source: environment variables loaded via `pydantic-settings` from `.env`.

Key variables:

- `APP_NAME`
- `DEBUG`
- `DATABASE_URL`
- `POSTGRES_PASSWORD` (used by compose)

Default DB URL:

```text
postgresql+asyncpg://postgres:password@localhost:5432/decision_engine
```

## Data Access Pattern

- Endpoints call services
- Services call repositories
- Repositories execute SQLAlchemy queries
- ORM models map to PostgreSQL tables

This pattern keeps HTTP concerns, business logic, and persistence logic separate.

## Request Flow (Decision Evaluation)

```mermaid
sequenceDiagram
  participant C as Client
  participant E as Decisions Endpoint
  participant S as DecisionService
  participant R as RuleRepository
  participant G as Rules Engine
  participant D as DecisionRepository
  participant A as AuditLogRepository

  C->>E: POST /api/v1/decisions/evaluate
  E->>S: validate DecisionRequest and call evaluate()
  S->>R: get_all_active(category)
  R-->>S: rules sorted by priority desc
  S->>G: evaluate_rules(payload, rules)
  G-->>S: outcome, triggered, reasons, risk_score, normalized_score
  S->>D: persist decision record
  S->>A: persist DECISION_EVALUATED audit event
  S-->>E: DecisionResponse
  E-->>C: 201 Created
```

## Error Handling

Global handlers in `app/main.py`:

- Validation errors (`422`) are returned in a frontend-friendly shape
- Unhandled exceptions (`500`) return a safe generic message

## Observability

- Structured logging format is configured in `app/core/observability.py`
- Request-level correlation is handled by `request_id` middleware in `app/main.py`
- Every HTTP response includes `X-Request-ID`
- Decision evaluation flow logs start/completion events with outcome and score metadata
- Business audit history remains stored in `audit_logs` (separate from technical logs)

## Testing

Run tests:

```bash
pytest tests/ -v
```

Current tests focus on rules engine behavior.
