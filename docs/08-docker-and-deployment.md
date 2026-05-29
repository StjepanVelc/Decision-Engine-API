# Docker and Deployment

## Container Strategy

The project uses a multi-stage Docker build:

1. `frontend-builder` (Node 20 Alpine)
2. `builder` (Python 3.12 slim, installs dependencies)
3. `runtime` (Python 3.12 slim, non-root user)

Final container serves:

- FastAPI backend
- built frontend static assets

## Build Image

```bash
docker build -t stipe35/decision-engine-api:latest .
```

## Run with Compose

```bash
docker compose up --build
```

Services:

- `db` (PostgreSQL 16-alpine)
- `api` (Decision Engine image)

Exposed ports:

- `5432` -> PostgreSQL
- `8000` -> App and API

## Environment in Compose

`api` service config:

- `DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@db:5432/decision_engine`
- `APP_NAME=Decision Engine API`
- `DEBUG=false`

## Health and Startup Ordering

`db` has healthcheck via `pg_isready`.

`api` waits for healthy DB using:

```yaml
depends_on:
  db:
    condition: service_healthy
```

## Production Notes

- Container runs as non-root user
- Keep `.env` out of version control
- Pin image tags for stable deployments
- Add CI pipeline for image build, scan, and publish
- Consider reverse proxy (Nginx/Traefik) for TLS and domain routing
