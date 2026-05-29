# Troubleshooting

## Docker Desktop Does Not Start (Windows)

Typical causes:

- WSL2 backend not installed or not running
- Hyper-V / virtualization disabled in BIOS
- Docker service stuck after update

Checks:

```powershell
docker version
docker info
wsl --status
```

If Docker is unavailable, run project locally (Python + Node + PostgreSQL) as fallback.

## `psql` Migration Works but VS Code Shows SQL Errors

Cause:

- MSSQL extension validates SQL as SQL Server dialect, not PostgreSQL

Resolution:

- Treat `psql` execution output as authoritative
- Optionally disable MSSQL rich SQL features for this workspace

## Frontend Cannot Reach Backend

Symptoms:

- network error in UI
- requests to `/api` fail in browser

Checks:

1. Backend running on `http://localhost:8000`
2. Frontend running on `http://localhost:5173`
3. Vite proxy exists in `frontend/vite.config.ts`

## DB Connection Errors in Backend

Check:

- `.env` has valid `DATABASE_URL`
- PostgreSQL user/password/database are correct
- DB host/port reachable

Quick check:

```powershell
psql -U postgres -d decision_engine -h localhost -p 5432
```

## CORS Issues

CORS origins are set in `app/main.py`.

Allowed local origins include:

- `http://localhost:5173`
- `http://localhost:4173`
- `http://localhost:3000`

If you use a different frontend port, add it to CORS config.

## Common API Validation Error (422)

Use response `details` field to locate invalid input.

Examples:

- missing `payload`
- invalid `operator`
- missing both `expression` and legacy triple (`field`, `operator`, `value`)
