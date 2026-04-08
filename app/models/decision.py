import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The raw JSON payload that was evaluated
    payload = Column(JSONB, nullable=False)

    # Final decision: "APPROVE", "REJECT", "REVIEW"
    outcome = Column(String(20), nullable=False)

    # Which rules triggered and their individual outcomes
    triggered_rules = Column(JSONB, nullable=False, default=list)

    # Human-readable explanation of the decision
    reasons = Column(JSONB, nullable=False, default=list)

    # Number of rules evaluated
    rules_evaluated = Column(Integer, nullable=False, default=0)

    # Accumulated risk score from all triggered rules
    risk_score = Column(Integer, nullable=False, default=0)

    # Normalized score: (risk_score / max_possible_score) * 100, or 0 if no active rules
    normalized_score = Column(Integer, nullable=False, default=0)

    # Optional external reference (e.g. transaction ID, user ID)
    reference_id = Column(String(100), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
