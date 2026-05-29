# Rules Engine

Core implementation: `app/services/rules_engine.py`

## Supported Rule Types

### 1) Expression rules (DSL)

Uses `expression` string, for example:

```text
amount > 10000 and country in ['NG', 'KP']
```

### 2) Legacy rules

Uses `field`, `operator`, `value`.

Example:

```json
{
  "field": "amount",
  "operator": "gt",
  "value": 10000
}
```

## Evaluation Order

Rules are loaded sorted by `priority DESC`.

For each rule:

1. Try to evaluate expression rule, or fallback to legacy mode
2. If evaluation fails, rule is skipped and logged (safe evaluation)
3. If rule matches and `hard_stop = true`, return immediate `REJECT`
4. Otherwise add `weight` to cumulative `risk_score`

## Legacy Operators

- `gt`, `lt`, `gte`, `lte`
- `eq`, `neq`
- `in`, `not_in`
- `contains`, `not_contains`

## Dot-Notation Support

Nested payload paths are supported in legacy mode.

Examples:

- `user.age`
- `transaction.metadata.score`

## Outcome Logic

Thresholds are based on cumulative `risk_score`:

- `risk_score >= 80` -> `REJECT`
- `risk_score >= 50` -> `REVIEW`
- else -> `APPROVE`

## Normalized Score

Formula:

```text
normalized_score = round((risk_score / max_possible_score) * 100)
```

Where `max_possible_score` is sum of weights for all active rules considered in that evaluation scope.

## Hard-Stop Rules

If a matching rule has `hard_stop = true`:

- outcome is immediately `REJECT`
- remaining rules are not evaluated
- triggered rule payload includes `hard_stop: true`

### Hard-Stop Example

Input payload:

```json
{
  "amount": 2500,
  "country": "KP",
  "user": { "age": 31 }
}
```

Matching high-priority rule:

```json
{
  "name": "sanctioned_country",
  "expression": "country in ['KP', 'IR']",
  "action": "REJECT",
  "weight": 100,
  "priority": 100,
  "hard_stop": true
}
```

Expected behavior:

- Engine returns `REJECT` immediately
- Lower-priority rules are not evaluated
- `triggered_rules[0].hard_stop` is `true`
- `reasons` contains hard-stop message

## Safe Evaluation

Each rule is wrapped in `try/except`.

- `ExpressionError` -> warning log and continue
- unexpected error -> error log and continue

A broken rule should not crash the whole decision pipeline.
