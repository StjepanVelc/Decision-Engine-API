# Database and Migrations

## Database

The project uses PostgreSQL with async SQLAlchemy ORM models.

Primary tables:

- `rules`
- `decisions`
- `audit_logs`

## Key Columns

### rules

- `name` (unique)
- `expression` (nullable)
- `field`, `operator`, `value` (nullable in expression mode)
- `action`
- `priority`
- `weight`
- `hard_stop`
- `is_active`
- `category`

### decisions

- `payload` (JSONB)
- `outcome`
- `triggered_rules` (JSONB)
- `reasons` (JSONB)
- `rules_evaluated`
- `risk_score`
- `normalized_score`
- `reference_id`

### audit_logs

- event metadata and JSON details for immutable change tracking

## Migrations in Repository

- `migrations/001_add_risk_scoring_and_expression.sql`
- `migrations/002_add_hard_stop_and_normalized_score.sql`

## Applying Migrations (Local PostgreSQL)

PowerShell example:

```powershell
$env:PGPASSWORD = "yourpassword"
psql -U postgres -d decision_engine -f "migrations/001_add_risk_scoring_and_expression.sql"
psql -U postgres -d decision_engine -f "migrations/002_add_hard_stop_and_normalized_score.sql"
```

## Note on SQL IntelliSense in VS Code

If MSSQL extension validates `.sql` files as SQL Server syntax, PostgreSQL statements may appear as editor errors even when they execute correctly in `psql`.

Use `psql` execution result as source of truth for PostgreSQL migrations.

## Schema Initialization

At application startup, SQLAlchemy runs:

```python
Base.metadata.create_all
```

This initializes missing tables. Migration files are still useful for controlled schema evolution in existing environments.
