# API Reference

Base path: `/api/v1`

## Health

### GET /health

Returns service status and version.

Note: this endpoint is global (outside `/api/v1`).

## Rules

Authentication for rule management endpoints:

- `POST /rules/`, `PATCH /rules/{rule_id}`, and `DELETE /rules/{rule_id}` require header `X-API-Key`
- Value must match server setting `RULES_ADMIN_API_KEY`

### POST /rules/
Create a new rule.

Request body (minimal legacy example):

```json
{
  "name": "high_amount",
  "field": "amount",
  "operator": "gt",
  "value": 10000,
  "action": "REVIEW",
  "priority": 10,
  "weight": 30,
  "hard_stop": false,
  "is_active": true,
  "category": "fraud"
}
```

Request body (expression example):

```json
{
  "name": "sanctioned_country",
  "expression": "country in ['KP', 'IR']",
  "action": "REJECT",
  "priority": 100,
  "weight": 100,
  "hard_stop": true,
  "category": "fraud"
}
```

### GET /rules/
List rules.

Query params:

- `skip` (default `0`)
- `limit` (default `100`, max `500`)

### GET /rules/{rule_id}
Get one rule by UUID.

### PATCH /rules/{rule_id}
Partially update a rule.

### DELETE /rules/{rule_id}
Delete a rule.

Returns `204 No Content`.

## Decisions

### POST /decisions/evaluate
Evaluate payload against active rules.

Request body:

```json
{
  "payload": {
    "amount": 15000,
    "country": "NG",
    "user": { "age": 17 }
  },
  "reference_id": "txn_abc123",
  "category": "fraud"
}
```

Response body shape:

```json
{
  "id": "uuid",
  "outcome": "REJECT",
  "risk_score": 85,
  "normalized_score": 85,
  "triggered_rules": [
    {
      "rule_id": "uuid",
      "rule_name": "high_amount",
      "action": "REVIEW",
      "weight": 30,
      "hard_stop": false,
      "match_detail": "amount gt 10000 (actual: 15000)"
    }
  ],
  "reasons": ["..."],
  "rules_evaluated": 6,
  "reference_id": "txn_abc123",
  "created_at": "2026-01-01T12:00:00Z"
}
```

### GET /decisions/
List decisions (newest first).

Query params:

- `skip` (default `0`)
- `limit` (default `100`, max `500`)

### GET /decisions/{decision_id}
Get one decision by UUID.

### GET /decisions/reference/{reference_id}
List decisions by external reference id.

## Stats

### GET /stats/
Returns aggregate counts and rates for outcomes.

## Error Model

Validation and API errors are returned in normalized format:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Request validation failed.",
  "details": [
    { "field": "payload.amount", "message": "Field required" }
  ]
}
```

For unexpected server errors:

```json
{
  "code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred. Please try again.",
  "details": null
}
```

## Response Headers

- `X-Request-ID` is returned on every response.
- Use this value to correlate client calls with backend structured logs.
