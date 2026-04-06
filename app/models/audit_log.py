import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Vrsta događaja: DECISION_EVALUATED, RULE_CREATED, RULE_UPDATED, RULE_DELETED
    event_type = Column(String(50), nullable=False, index=True)

    # Na koji entitet se odnosi: "decision" | "rule"
    entity_type = Column(String(50), nullable=False)

    # ID entiteta (decision.id ili rule.id)
    entity_id = Column(String(100), nullable=False, index=True)

    # Detalji događaja u JSON obliku
    details = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
