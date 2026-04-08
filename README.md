# Decision Engine API

A **rule-based decision engine** built with **FastAPI + React** for evaluating arbitrary JSON payloads against configurable business rules and returning an audited `APPROVE / REVIEW / REJECT` outcome.

> A portfolio project showcasing layered backend architecture, asynchronous Python, domain-oriented design, weighted risk scoring, hard-stop rules, normalized scoring, a safe DSL expression evaluator, immutable audit logging, real-time statistics, and a React + shadcn/ui dashboard — all containerized and served from a single deployment unit.

---

## Overview

The Decision Engine API models dynamic decision-making systems where rules can be modified without redeploying code.

Typical use cases include:

* fraud detection
* compliance validation
* pricing decisions
* internal policy enforcement

The system supports both structured rules and expression-based DSL rules, while ensuring full auditability of every decision.

---

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (React + shadcn/ui)           │
├─────────────────────────────────────────┤
│  API Layer (FastAPI)                    │
├─────────────────────────────────────────┤
│  Service Layer (Decision Engine)        │
├─────────────────────────────────────────┤
│  Repository Layer (PostgreSQL)          │
└─────────────────────────────────────────┘
```

---

## Core Features

* Configurable rules via API (no redeploy required)
* DSL expressions (`amount > 10000 and country in ['NG']`)
* Legacy rule support (field/operator/value)
* Safe AST-based expression evaluator (no eval)
* Risk scoring system (weighted rules)
* Normalized score (0–100%)
* Hard-stop rules (instant REJECT)
* Threshold-based decisions
* Category-based rule filtering
* Immutable audit logging
* Full decision traceability
* React dashboard (rules + evaluation + stats)
* Dockerized full-stack deployment

---

## Decision Flow

1. Load active rules (sorted by priority)
2. Evaluate rules (DSL or legacy mode)
3. If hard-stop rule matches → immediate REJECT
4. Otherwise accumulate `risk_score`
5. Apply thresholds to determine outcome
6. Store decision + audit log

---

## Risk Scoring

Each rule has a `weight`.

```
risk_score = sum(weight of matched rules)
```

### Thresholds

| Score | Outcome |
| ----- | ------- |
| ≥ 80  | REJECT  |
| ≥ 50  | REVIEW  |
| < 50  | APPROVE |

---

### Normalized Score

```
normalized_score = round(risk_score / max_possible_score * 100)
```

Represents relative risk (0–100%).

---

### Hard-stop Rules

Rules with `hard_stop = true` immediately return:

```
REJECT
```

without evaluating further rules.

---

## DSL Expression Rules

Examples:

```
amount > 10000
country in ['NG', 'KP']
user.age < 18
amount > 5000 and verified == False
```

### Supported

* comparisons: >, <, >=, <=, ==, !=
* logical: and, or, not
* membership: in, not in
* dot notation: user.age
* arithmetic expressions

### Safety

* AST-based parser
* strict whitelist
* no eval / exec
* no imports or function calls

---

## Example

### Input

```json
{
  "amount": 15000,
  "country": "NG"
}
```

### Output

```json
{
  "outcome": "REJECT",
  "risk_score": 85,
  "normalized_score": 85
}
```

---

## API

### Rules

* POST `/rules/`
* GET `/rules/`
* PATCH `/rules/{id}`
* DELETE `/rules/{id}`

### Decisions

* POST `/decisions/evaluate`
* GET `/decisions/`

### Stats

* GET `/stats/`

---

## Audit Log

Every action is recorded:

* rule created / updated / deleted
* decision evaluated

Stored with metadata and timestamps.

---

## Tech Stack

* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* React + TypeScript
* Tailwind + shadcn/ui
* TanStack Query
* Docker

---

## Summary

This project demonstrates how to design a **configurable, auditable decision system** that separates business logic from code and supports real-world use cases such as fraud detection and compliance evaluation.
