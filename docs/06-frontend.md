# Frontend

Frontend location: `frontend/`

## Stack

- React 19 + TypeScript
- Vite
- TanStack Query
- React Router
- shadcn/ui + Tailwind CSS
- Axios

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Default dev URL: `http://localhost:5173`

## API Integration

HTTP client: `frontend/src/api/client.ts`

- Base URL: `/api/v1`
- JSON content type by default
- Response interceptor normalizes API/network errors

Vite proxy in `vite.config.ts` forwards `/api` to:

```text
http://localhost:8000
```

This avoids CORS issues in local development.

## Routes

Defined in `frontend/src/App.tsx`:

- `/` -> Dashboard
- `/rules` -> Rules management
- `/decisions` -> Decision history and detail panel
- `/evaluate` -> Manual payload evaluation UI

## UI Features by Page

### Dashboard

- Outcome counters and rates
- Visual charts for activity and distribution

### Rules

- Create, edit, delete rules
- Supports expression and legacy rule mode
- Configure `weight`, `priority`, `hard_stop`, `category`

### Decisions

- Decision history table
- Side panel with payload, triggered rules, and reasons
- Shows `risk_score` and `normalized_score`

### Evaluate

- JSON payload editor
- Evaluate on demand
- Displays outcome, scores, triggered rules, and reasons

## Build

```bash
cd frontend
npm run build
```

Output directory: `frontend/dist`
