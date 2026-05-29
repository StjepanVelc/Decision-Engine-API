from pathlib import Path
import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1.router import router
from app.core.config import settings
from app.core.observability import configure_logging, reset_request_id, set_request_id

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "A configurable, rule-based Decision Engine API. "
        "Define rules once via the Rules API, then evaluate any JSON payload "
        "to get an APPROVE / REVIEW / REJECT decision with full audit trail."
    ),
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:4173",   # Vite preview
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    token = set_request_id(request_id)
    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "request_completed method=%s path=%s duration_ms=%s",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        reset_request_id(token)

    response.headers["X-Request-ID"] = request_id
    return response


# ── Global error handlers ─────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert Pydantic 422 errors into a frontend-friendly format."""
    details = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = ".".join(str(item) for item in loc if item != "body") or None
        details.append({"field": field, "message": error.get("msg", "Validation error")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "details": details,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — never expose internal details to the frontend."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "details": None,
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.version}


# ── SPA / Static files ─────────────────────────────────────────────────────────
# Served only when the built frontend/dist exists (i.e. in Docker / production).
_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if _FRONTEND_DIST.exists():
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        target = _FRONTEND_DIST / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(_FRONTEND_DIST / "index.html")
