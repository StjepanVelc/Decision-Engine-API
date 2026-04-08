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

    # ── DSL expression (if set, field/operator/value are ignored) ────────────
    expression: Optional[str] = Field(
        default=None,
        examples=["transaction_amount > 10000 and country in ['NG', 'KP']"],
    )

    # ── Legacy condition fields (required when expression is not set) ────────
    field: Optional[str] = Field(default=None, min_length=1, max_length=100, examples=["transaction_amount"])
    operator: Optional[str] = Field(default=None, examples=["gt"])
    value: Optional[Any] = Field(default=None, examples=[10000])

    action: str = Field(default="REJECT", examples=["REJECT"])
    priority: float = Field(default=0.0, ge=0.0, le=1000.0)
    weight: int = Field(default=10, ge=0, le=1000, examples=[25])
    hard_stop: bool = Field(
        default=False,
        description="If True, a match immediately returns REJECT and stops further evaluation.",
        examples=[False],
    )
    is_active: bool = True
    category: Optional[str] = Field(default=None, max_length=50, examples=["fraud"])

    @field_validator("name")
    @classmethod
    def strip_and_no_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("cannot be blank")
        return v

    @field_validator("field")
    @classmethod
    def strip_field(cls, v: Optional[str]) -> Optional[str]:
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
    def validate_action(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_ACTIONS:
            raise ValueError(f"invalid action '{v}'. Valid: {sorted(VALID_ACTIONS)}")
        return v

    @model_validator(mode="after")
    def validate_expression_or_legacy(self) -> "RuleCreate":
        has_expression = bool(self.expression and self.expression.strip())
        has_legacy = self.field is not None and self.operator is not None and self.value is not None

        if not has_expression and not has_legacy:
            raise ValueError(
                "Either 'expression' or all three of 'field', 'operator', 'value' must be provided"
            )

        # Validate list-vs-scalar constraint only for legacy rules
        if not has_expression and self.operator is not None and self.value is not None:
            if self.operator in LIST_OPERATORS and not isinstance(self.value, list):
                raise ValueError(
                    f"operator '{self.operator}' requires value to be a list, e.g. [\"US\", \"DE\"]"
                )
            if self.operator not in LIST_OPERATORS and isinstance(self.value, list):
                raise ValueError(f"operator '{self.operator}' does not accept a list value")

        return self


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    expression: Optional[str] = None
    field: Optional[str] = Field(default=None, min_length=1, max_length=100)
    operator: Optional[str] = None
    value: Optional[Any] = None
    action: Optional[str] = None
    priority: Optional[float] = Field(default=None, ge=0.0, le=1000.0)
    weight: Optional[int] = Field(default=None, ge=0, le=1000)
    hard_stop: Optional[bool] = None
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
    expression: Optional[str]
    field: Optional[str]
    operator: Optional[str]
    value: Optional[Any]
    action: str
    priority: float
    weight: int
    hard_stop: bool
    is_active: bool
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
