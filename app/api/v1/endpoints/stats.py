from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.decision import Decision
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Vraća agregatnu statistiku svih donesenih odluka:
    - ukupni broj evaluacija
    - broj i postotak APPROVE / REVIEW / REJECT
    - success_rate (postotak odobrenih)
    """
    result = await db.execute(
        select(
            func.count().label("total"),
            func.count(Decision.outcome).filter(Decision.outcome == "APPROVE").label("approve"),
            func.count(Decision.outcome).filter(Decision.outcome == "REVIEW").label("review"),
            func.count(Decision.outcome).filter(Decision.outcome == "REJECT").label("reject"),
        )
    )
    row = result.one()

    total: int = row.total or 0
    approve: int = row.approve or 0
    review: int = row.review or 0
    reject: int = row.reject or 0

    def pct(n: int) -> float:
        return round(n / total * 100, 2) if total > 0 else 0.0

    return StatsResponse(
        total_decisions=total,
        approve_count=approve,
        review_count=review,
        reject_count=reject,
        approve_rate=pct(approve),
        review_rate=pct(review),
        reject_rate=pct(reject),
        success_rate=pct(approve),
    )
