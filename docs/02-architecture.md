# Architecture

## High-Level Components

The project is split into a backend API, a React frontend, and PostgreSQL storage.

```text
Frontend (React + Vite + TanStack Query)
          |
          v
FastAPI API Layer (app/api)
          |
          v
Service Layer (app/services)
          |
          v
Repository Layer (app/repositories)
          |
          v
PostgreSQL (app/models + SQLAlchemy async)
```

## Backend Layers

### API Layer

Location: `app/api/v1/endpoints`

Responsibilities:

- HTTP routing and request parsing
- Input validation and response models
- Status code and error mapping

### Service Layer

Location: `app/services`

Responsibilities:

- Business logic orchestration
- Rule evaluation and scoring
- Decision creation and audit logging

### Repository Layer

Location: `app/repositories`

Responsibilities:

- Database reads and writes
- Query composition and filtering
- Persistence abstraction for services

## Runtime Flow

1. Client calls `POST /api/v1/decisions/evaluate`
2. Endpoint validates `DecisionRequest`
3. `DecisionService` loads active rules (optional category filter)
4. `rules_engine.evaluate_rules(...)` executes decision logic
5. Decision is stored in `decisions`
6. Audit event is written to `audit_logs`
7. API returns `DecisionResponse`

## Key Design Decisions

- Async stack end-to-end (FastAPI + SQLAlchemy async + asyncpg)
- Rules editable at runtime via API (no redeploy needed)
- Safe expression evaluator based on Python AST (no `eval`)
- Layered structure to keep concerns isolated
- Docker image serves both API and built SPA in one deployment unit
