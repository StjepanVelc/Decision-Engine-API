from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import Decision


class DecisionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, decision: Decision) -> Decision:
        self.db.add(decision)
        await self.db.commit()
        await self.db.refresh(decision)
        return decision

    async def get_by_id(self, decision_id: UUID) -> Optional[Decision]:
        result = await self.db.execute(select(Decision).where(Decision.id == decision_id))
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference_id: str) -> List[Decision]:
        result = await self.db.execute(
            select(Decision)
            .where(Decision.reference_id == reference_id)
            .order_by(Decision.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Decision]:
        result = await self.db.execute(
            select(Decision).order_by(Decision.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
