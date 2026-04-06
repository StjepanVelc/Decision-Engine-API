from fastapi import APIRouter

from app.api.v1.endpoints import decisions, rules, stats

router = APIRouter(prefix="/api/v1")
router.include_router(rules.router)
router.include_router(decisions.router)
router.include_router(stats.router)
