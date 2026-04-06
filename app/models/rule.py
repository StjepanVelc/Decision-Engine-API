import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (
        CheckConstraint(
            "operator IN ('gt','lt','gte','lte','eq','neq','in','not_in','contains','not_contains')",
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
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # e.g. "transaction_amount", "country", "user_age"
    field = Column(String(100), nullable=False)

    # operator: "gt", "lt", "gte", "lte", "eq", "neq", "in", "not_in", "contains", "not_contains"
    operator = Column(String(20), nullable=False)

    # value to compare against (stored as JSON to support lists, numbers, strings)
    value = Column(JSONB, nullable=False)

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
