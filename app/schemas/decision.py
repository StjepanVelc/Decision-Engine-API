from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    payload: Dict[str, Any] = Field(
        ...,
        examples=[
            {
                "transaction_amount": 15000,
                "country": "NG",
                "user_age": 18,
                "ip_country": "RU",
                "device_fingerprint_new": True,
            }
        ],
    )
    reference_id: Optional[str] = Field(
        default=None,
        examples=["txn_abc123"],
        description="Optional external reference (transaction ID, user ID, etc.)",
    )
    category: Optional[str] = Field(
        default=None,
        examples=["fraud"],
        description="Evaluate only rules in this category. Omit for all rules.",
    )


class DecisionResponse(BaseModel):
    id: UUID
    outcome: str
    risk_score: int
    normalized_score: int
    triggered_rules: List[Dict[str, Any]]
    reasons: List[str]
    rules_evaluated: int
    reference_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
