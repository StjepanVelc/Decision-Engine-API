from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rule import Rule
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.rule_repository import RuleRepository
from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate


class RuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RuleRepository(db)
        self.audit = AuditLogRepository(db)

    async def create_rule(self, data: RuleCreate) -> RuleResponse:
        rule = Rule(**data.model_dump())
        saved = await self.repo.create(rule)
        await self.audit.log(
            event_type="RULE_CREATED",
            entity_type="rule",
            entity_id=str(saved.id),
            details={"name": str(saved.name), "category": str(saved.category or "")},
        )
        return RuleResponse.model_validate(saved)

    async def get_rule(self, rule_id: UUID) -> Optional[RuleResponse]:
        rule = await self.repo.get_by_id(rule_id)
        if rule is None:
            return None
        return RuleResponse.model_validate(rule)

    async def list_rules(self, skip: int = 0, limit: int = 100) -> List[RuleResponse]:
        rules = await self.repo.get_all(skip=skip, limit=limit)
        return [RuleResponse.model_validate(r) for r in rules]

    async def update_rule(self, rule_id: UUID, data: RuleUpdate) -> Optional[RuleResponse]:
        updates = data.model_dump(exclude_unset=True)
        rule = await self.repo.update(rule_id, updates)
        if rule is None:
            return None
        await self.audit.log(
            event_type="RULE_UPDATED",
            entity_type="rule",
            entity_id=str(rule_id),
            details={"changed_fields": list(updates.keys())},
        )
        return RuleResponse.model_validate(rule)

    async def delete_rule(self, rule_id: UUID) -> bool:
        deleted = await self.repo.delete(rule_id)
        if deleted:
            await self.audit.log(
                event_type="RULE_DELETED",
                entity_type="rule",
                entity_id=str(rule_id),
                details={},
            )
        return deleted
