from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import Rule


class RuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, rule: Rule) -> Rule:
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: UUID) -> Optional[Rule]:
        result = await self.db.execute(select(Rule).where(Rule.id == rule_id))
        return result.scalar_one_or_none()

    async def get_all_active(self, category: Optional[str] = None) -> List[Rule]:
        query = select(Rule).where(Rule.is_active.is_(True)).order_by(Rule.priority.desc())
        if category:
            query = query.where(Rule.category == category)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Rule]:
        result = await self.db.execute(
            select(Rule).order_by(Rule.priority.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, rule_id: UUID, updates: dict) -> Optional[Rule]:
        await self.db.execute(update(Rule).where(Rule.id == rule_id).values(**updates))
        await self.db.commit()
        return await self.get_by_id(rule_id)

    async def delete(self, rule_id: UUID) -> bool:
        result = await self.db.execute(delete(Rule).where(Rule.id == rule_id))
        await self.db.commit()
        return result.rowcount > 0
