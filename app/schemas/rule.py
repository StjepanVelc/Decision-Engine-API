from datetime import datetime
from typing import Any, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

VALID_OPERATORS = {"gt", "lt", "gte", "lte", "eq", "neq", "in", "not_in", "contains", "not_contains"}
VALID_ACTIONS = {"APPROVE", "REVIEW", "REJECT"}
LIST_OPERATORS = {"in", "not_in"}


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["high_transaction_amount"])
    description: Optional[str] = Field(default=None, max_length=500)
    field: str = Field(..., min_length=1, max_length=100, examples=["transaction_amount"])
    operator: str = Field(..., examples=["gt"])
    value: Any = Field(..., examples=[10000])
    action: str = Field(default="REJECT", examples=["REJECT"])
    priority: float = Field(default=0.0, ge=0.0, le=1000.0)
    is_active: bool = True
    category: Optional[str] = Field(default=None, max_length=50, examples=["fraud"])

    @field_validator("name", "field")
    @classmethod
    def strip_and_no_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("cannot be blank")
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: str) -> str:
        if v not in VALID_OPERATORS:
            raise ValueError(f"invalid operator '{v}'. Valid: {sorted(VALID_OPERATORS)}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_ACTIONS:
            raise ValueError(f"invalid action '{v}'. Valid: {sorted(VALID_ACTIONS)}")
        return v

    @model_validator(mode="after")
    def validate_value_for_operator(self) -> "RuleCreate":
        if self.operator in LIST_OPERATORS and not isinstance(self.value, list):
            raise ValueError(f"operator '{self.operator}' requires value to be a list, e.g. [\"US\", \"DE\"]")
        if self.operator not in LIST_OPERATORS and isinstance(self.value, list):
            raise ValueError(f"operator '{self.operator}' does not accept a list value")
        return self


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    field: Optional[str] = Field(default=None, min_length=1, max_length=100)
    operator: Optional[str] = None
    value: Optional[Any] = None
    action: Optional[str] = None
    priority: Optional[float] = Field(default=None, ge=0.0, le=1000.0)
    is_active: Optional[bool] = None
    category: Optional[str] = Field(default=None, max_length=50)

    @field_validator("name", "field")
    @classmethod
    def strip_and_no_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("cannot be blank")
        return v

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_OPERATORS:
            raise ValueError(f"invalid operator '{v}'. Valid: {sorted(VALID_OPERATORS)}")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.upper()
            if v not in VALID_ACTIONS:
                raise ValueError(f"invalid action '{v}'. Valid: {sorted(VALID_ACTIONS)}")
        return v


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
