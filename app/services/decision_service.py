from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision import Decision
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.decision_repository import DecisionRepository
from app.repositories.rule_repository import RuleRepository
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.services.rules_engine import evaluate_rules


class DecisionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = RuleRepository(db)
        self.decision_repo = DecisionRepository(db)
        self.audit = AuditLogRepository(db)

    async def evaluate(
        self,
        request: DecisionRequest,
        category: Optional[str] = None,
    ) -> DecisionResponse:
        rules = await self.rule_repo.get_all_active(category=category)

        outcome, triggered, reasons, risk_score, normalized_score = evaluate_rules(request.payload, rules)

        record = Decision(
            payload=request.payload,
            outcome=outcome,
            triggered_rules=triggered,
            reasons=reasons,
            rules_evaluated=len(rules),
            risk_score=risk_score,
            normalized_score=normalized_score,
            reference_id=request.reference_id,
        )
        saved = await self.decision_repo.create(record)

        await self.audit.log(
            event_type="DECISION_EVALUATED",
            entity_type="decision",
            entity_id=str(saved.id),
            details={
                "outcome": outcome,
                "risk_score": risk_score,
                "normalized_score": normalized_score,
                "rules_evaluated": len(rules),
                "triggered_count": len(triggered),
                "reference_id": request.reference_id,
                "category": category,
            },
        )

        return DecisionResponse.model_validate(saved)
