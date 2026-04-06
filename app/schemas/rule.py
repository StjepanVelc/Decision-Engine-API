from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    name: str = Field(..., max_length=100, examples=["high_transaction_amount"])
    description: Optional[str] = None
    field: str = Field(..., examples=["transaction_amount"])
    operator: str = Field(..., examples=["gt"])
    value: Any = Field(..., examples=[10000])
    action: str = Field(default="REJECT", examples=["REJECT"])
    priority: float = Field(default=0.0, ge=0.0)
    is_active: bool = True
    category: Optional[str] = Field(default=None, examples=["fraud"])


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None
    action: Optional[str] = None
    priority: Optional[float] = Field(default=None, ge=0.0)
    is_active: Optional[bool] = None
    category: Optional[str] = None


class RuleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    field: str
    operator: str
    value: Any
    action: str
    priority: float
    is_active: bool
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
