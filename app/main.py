from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router
from app.core.config import settings
from app.core.database import Base, engine
import app.models.rule  # noqa: F401 — registracija modela
import app.models.decision  # noqa: F401
import app.models.audit_log  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "A configurable, rule-based Decision Engine API. "
        "Define rules once via the Rules API, then evaluate any JSON payload "
        "to get an APPROVE / REVIEW / REJECT decision with full audit trail."
    ),
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.version}
