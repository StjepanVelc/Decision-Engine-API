# Quick Start

This guide explains how to run the project in two modes:

- Local development (backend and frontend separately)
- Docker Compose (full stack)

## Prerequisites

### Local development

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+ (or compatible)

### Docker mode

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose v2

## Clone and Configure

```bash
git clone <your-repo-url>
cd "Decision Engine API"
copy .env.example .env
# cp .env.example .env   # Linux/macOS
```

Update `.env` values:

```env
APP_NAME=Decision Engine API
DEBUG=false
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/decision_engine
POSTGRES_PASSWORD=yourpassword
```

## Run Locally

### 1) Backend

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

Create database once:

```sql
CREATE DATABASE decision_engine;
```

Start API:

```bash
uvicorn app.main:app --reload
```

Backend URLs:

- API: http://localhost:8000/api/v1/
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- App: http://localhost:5173

## Run with Docker Compose

```bash
docker compose up --build
```

URLs in Docker mode:

- App + API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

Stop containers:

```bash
docker compose down
```

Remove containers and DB volume:

```bash
docker compose down -v
```

## Smoke Test

Create one rule and evaluate one payload.

### Create rule

```bash
curl -X POST http://localhost:8000/api/v1/rules/ \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"high_amount\",\"field\":\"amount\",\"operator\":\"gt\",\"value\":10000,\"action\":\"REVIEW\",\"priority\":10,\"weight\":30}"
```

### Evaluate payload

```bash
curl -X POST http://localhost:8000/api/v1/decisions/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"payload\":{\"amount\":15000},\"reference_id\":\"demo-1\",\"category\":null}"
```
