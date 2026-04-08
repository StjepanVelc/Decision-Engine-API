# Decision Engine API

A **rule-based Decision Engine** built with **FastAPI + React**, designed to evaluate arbitrary JSON payloads against configurable rules and return an audited `APPROVE / REVIEW / REJECT` decision.

> Portfolio project demonstrating 3-layer backend architecture, async Python, domain-driven design, audit logging, real-time statistics, a React + shadcn/ui frontend dashboard, and full Docker containerization — all served from a single container.

---

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + shadcn/ui)           │
│  src/pages/ · src/components/           │
│  TanStack Query · React Router          │
├─────────────────────────────────────────┤
│  Layer 1 – API (Presentation)           │
│  app/api/v1/endpoints/                  │
│  FastAPI routes, request/response       │
├─────────────────────────────────────────┤
│  Layer 2 – Services (Business Logic)    │
│  app/services/                          │
│  Rules Engine, Decision Service         │
├─────────────────────────────────────────┤
│  Layer 3 – Repositories (Data Access)  │
│  app/repositories/  +  app/models/      │
│  SQLAlchemy async ORM, PostgreSQL       │
└─────────────────────────────────────────┘
```

---

## Features

- **Configurable rules** – create/update/delete rules via REST API (no redeploy needed)
- **Operators**: `gt`, `lt`, `gte`, `lte`, `eq`, `neq`, `in`, `not_in`, `contains`, `not_contains`
- **Priority-based evaluation** – rules run highest priority first; most severe outcome wins
- **Category filtering** – evaluate only `fraud`, `compliance`, or `pricing` rules
- **Decision audit trail** – every evaluation stored with full payload, triggered rules, and human-readable reasons
- **Immutable audit log** – every create/update/delete on rules and every decision is written to a separate `audit_logs` table with event type, entity ID, and metadata
- **Statistics endpoint** – real-time APPROVE / REVIEW / REJECT counts and success rate across all decisions
- **Dot-notation field access** – evaluate nested JSON fields like `user.age`
- **React dashboard** – shadcn/ui interface for managing rules, browsing decisions, and evaluating payloads in real-time
- **Docker ready** – multi-stage Dockerfile (Node + Python), Docker Compose with PostgreSQL, frontend and backend served from a single container on port 8000

---

## Quick Start

### Option A — Docker (recommended)

> No Python, Node.js, or PostgreSQL installation needed.

```bash
git clone <repo>
cd "Decision Engine API"

# Copy and configure environment
copy .env.example .env
# Edit .env and set POSTGRES_PASSWORD

docker compose up
```

Or pull directly from Docker Hub:

```bash
docker pull stipe35/decision-engine-api:latest
docker compose up
```

| URL | Description |
|-----|-------------|
| **http://localhost:8000** | React frontend dashboard |
| **http://localhost:8000/docs** | Swagger / OpenAPI UI |
| **http://localhost:8000/api/v1/** | REST API root |

---

### Option B — Local development (frontend + backend separately)

**Terminal 1 — Backend:**

**Prerequisites:** Python 3.12+, PostgreSQL

```bash
git clone <repo>
cd "Decision Engine API"

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Configure `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/decision_engine
```

Create the database:
```sql
CREATE DATABASE decision_engine;
```

Run the backend:
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

| URL | Description |
|-----|-------------|
| **http://localhost:5173** | React dev server (with HMR) |
| **http://localhost:8000/docs** | Swagger UI |

---

## API Overview

### Rules

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/rules/` | Create a rule |
| `GET` | `/api/v1/rules/` | List all rules |
| `GET` | `/api/v1/rules/{id}` | Get rule by ID |
| `PATCH` | `/api/v1/rules/{id}` | Update rule |
| `DELETE` | `/api/v1/rules/{id}` | Delete rule |

### Decisions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/decisions/evaluate` | Evaluate payload → decision |
| `GET` | `/api/v1/decisions/` | List all decisions |
| `GET` | `/api/v1/decisions/{id}` | Get decision by ID |
| `GET` | `/api/v1/decisions/reference/{ref}` | Get by external reference |

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/stats/` | Aggregate decision statistics |

---

## Example: Fraud Detection

### 1. Create rules

```json
POST /api/v1/rules/
{
  "name": "high_transaction_amount",
  "field": "transaction_amount",
  "operator": "gt",
  "value": 10000,
  "action": "REJECT",
  "priority": 10,
  "category": "fraud"
}
```

```json
POST /api/v1/rules/
{
  "name": "high_risk_country",
  "field": "country",
  "operator": "in",
  "value": ["NG", "KP"],
  "action": "REVIEW",
  "priority": 5,
  "category": "fraud"
}
```

### 2. Evaluate a transaction

```json
POST /api/v1/decisions/evaluate
{
  "payload": {
    "transaction_amount": 15000,
    "country": "NG",
    "user_age": 25
  },
  "reference_id": "txn_abc123",
  "category": "fraud"
}
```

### 3. Response

```json
{
  "id": "...",
  "outcome": "REJECT",
  "triggered_rules": [
    {
      "rule_name": "high_transaction_amount",
      "action": "REJECT",
      "field": "transaction_amount",
      "operator": "gt",
      "threshold": 10000,
      "actual_value": 15000
    },
    {
      "rule_name": "high_risk_country",
      "action": "REVIEW",
      "field": "country",
      "operator": "in",
      "threshold": ["NG", "KP"],
      "actual_value": "NG"
    }
  ],
  "reasons": [
    "Rule 'high_transaction_amount' triggered: transaction_amount gt 10000 (actual: 15000) → REJECT",
    "Rule 'high_risk_country' triggered: country in ['NG', 'KP'] (actual: NG) → REVIEW"
  ],
  "rules_evaluated": 2,
  "reference_id": "txn_abc123"
}
```

---

## Audit Log

Every significant action is automatically recorded in the `audit_logs` table — no extra API calls needed.

| Event | Trigger |
|-------|---------|
| `DECISION_EVALUATED` | Any call to `POST /decisions/evaluate` |
| `RULE_CREATED` | `POST /rules/` |
| `RULE_UPDATED` | `PATCH /rules/{id}` |
| `RULE_DELETED` | `DELETE /rules/{id}` |

Each entry stores: `event_type`, `entity_type`, `entity_id`, `details` (JSON), `created_at`.

---

## Statistics

```
GET /api/v1/stats/
```

```json
{
  "total_decisions": 150,
  "approve_count": 120,
  "review_count": 18,
  "reject_count": 12,
  "approve_rate": 80.0,
  "review_rate": 12.0,
  "reject_rate": 8.0,
  "success_rate": 80.0
}
```

All percentages are calculated server-side with a single aggregation query.

---

## Frontend Dashboard

The React dashboard is bundled into the Docker image and served automatically by FastAPI at **http://localhost:8000**.

### Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Stats cards (total, approved, reviewed, rejected) + outcome bar chart + recent activity chart |
| **Rules** | Table of all rules with create / edit (dialog) / delete. Supports all 10 operators and 3 actions. |
| **Decisions** | History table of all evaluations. Click any row to open a detail side-sheet with triggered rules and reasons. |
| **Evaluate** | Submit a JSON payload directly from the UI, see outcome, triggered rules, and reasons instantly. |

### Tech

Built with React 18 + TypeScript, **shadcn/ui** component library, Tailwind CSS v3, TanStack Query for server state, and Recharts for visualisations. The Vite dev proxy forwards all `/api/*` requests to the backend — no CORS config needed in development.

---

## Tests

```bash
pytest tests/ -v
```

---

## Database Schema

```
┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│    rules     │     │    decisions    │     │  audit_logs   │
├──────────────┤     ├─────────────────┤     ├───────────────┤
│ id (UUID)    │     │ id (UUID)       │     │ id (UUID)     │
│ name         │     │ payload (JSONB) │     │ event_type    │
│ field        │     │ outcome         │     │ entity_type   │
│ operator     │     │ triggered_rules │     │ entity_id     │
│ value (JSONB)│     │ reasons (JSONB) │     │ details (JSON)│
│ action       │     │ rules_evaluated │     │ created_at    │
│ priority     │     │ reference_id    │     └───────────────┘
│ is_active    │     │ created_at      │
│ category     │     └─────────────────┘
│ created_at   │
│ updated_at   │
└──────────────┘
```

---

## Docker

### Image on Docker Hub

```
docker.io/stipe35/decision-engine-api:latest
```

### Build locally

The Dockerfile uses a **3-stage multi-stage build**:
1. **`frontend-builder`** (Node 20 Alpine) — runs `npm ci && npm run build`
2. **`builder`** (Python 3.12 slim) — installs Python dependencies
3. **`runtime`** (Python 3.12 slim) — copies both compiled assets into the final image

```bash
docker build -t stipe35/decision-engine-api:latest .
```

### Run with Compose (API + PostgreSQL)

```bash
docker compose up          # foreground
docker compose up -d       # background
docker compose down        # stop and remove containers
docker compose down -v     # also remove the database volume
```

### Environment variables (docker-compose.yml)

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_PASSWORD` | `password` | PostgreSQL password |
| `DATABASE_URL` | auto-set from `POSTGRES_PASSWORD` | Full connection string |
| `DEBUG` | `false` | Enable SQLAlchemy query logging |

Set `POSTGRES_PASSWORD` in your `.env` file (copied from `.env.example`).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL + asyncpg |
| Validation | Pydantic v2 |
| Testing | pytest |
| Server | Uvicorn |
| Containerization | Docker + Docker Compose |
| Image Registry | Docker Hub (`stipe35/decision-engine-api`) |
| Frontend Framework | React 18 + TypeScript |
| UI Components | shadcn/ui + Tailwind CSS v3 |
| State Management | TanStack Query (React Query) |
| Forms | react-hook-form + Zod |
| Charts | Recharts |
| Routing | React Router v6 |
| HTTP Client | Axios |
