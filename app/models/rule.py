import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint(
            "operator IS NULL OR operator IN ('gt','lt','gte','lte','eq','neq','in','not_in','contains','not_contains')",
            name="ck_rules_operator",
        ),
        CheckConstraint(
            "action IN ('APPROVE','REVIEW','REJECT')",
            name="ck_rules_action",
        ),
        CheckConstraint(
            "priority >= 0",
            name="ck_rules_priority_positive",
        ),
        CheckConstraint(
            "weight >= 0",
            name="ck_rules_weight_positive",
        ),
        CheckConstraint(
            "expression IS NOT NULL OR (field IS NOT NULL AND operator IS NOT NULL AND value IS NOT NULL)",
            name="ck_rules_expression_or_legacy",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # ── Legacy condition fields (kept for backward compatibility) ─────────────
    # e.g. "transaction_amount", "country", "user_age"
    field = Column(String(100), nullable=True)

    # operator: "gt", "lt", "gte", "lte", "eq", "neq", "in", "not_in", "contains", "not_contains"
    operator = Column(String(20), nullable=True)

    # value to compare against (stored as JSON to support lists, numbers, strings)
    value = Column(JSONB, nullable=True)

    # ── DSL expression (takes priority over field/operator/value if set) ──────
    # e.g. "transaction_amount > 10000 and country in ['NG', 'KP']"
    expression = Column(Text, nullable=True)

    # ── Risk scoring ──────────────────────────────────────────────────────────
    # contribution to risk_score when this rule is triggered
    weight = Column(Integer, nullable=False, default=10)

    # if True: rule matching immediately returns REJECT, skipping further evaluation
    hard_stop = Column(Boolean, nullable=False, default=False)

    # decision outcome if this rule matches: "REJECT", "REVIEW", "APPROVE"
    action = Column(String(20), nullable=False, default="REJECT")

    # higher priority rules are evaluated first
    priority = Column(Float, nullable=False, default=0.0)

    is_active = Column(Boolean, nullable=False, default=True)

    category = Column(String(50), nullable=True)  # e.g. "fraud", "compliance", "pricing"

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
