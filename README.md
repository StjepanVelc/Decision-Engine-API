# Decision Engine API

A **rule-based Decision Engine** REST API built with **FastAPI + PostgreSQL**, designed to evaluate arbitrary JSON payloads against configurable rules and return an audited `APPROVE / REVIEW / REJECT` decision.

> Portfolio project demonstrating 3-layer architecture, async Python, domain-driven design, audit logging, and real-time statistics.

---

## Architecture

```
┌─────────────────────────────────────────┐
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

---

## Quick Start

### 1. Prerequisites

- Python 3.12+
- PostgreSQL running locally

### 2. Setup

```bash
git clone <repo>
cd "Decision Engine API"

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure database

Edit `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/decision_engine
```

Create the database in PostgreSQL:
```sql
CREATE DATABASE decision_engine;
```

### 4. Run

```bash
uvicorn app.main:app --reload
```

API docs available at: **http://localhost:8000/docs**

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

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL + asyncpg |
| Validation | Pydantic v2 |
| Testing | pytest |
| Server | Uvicorn |
