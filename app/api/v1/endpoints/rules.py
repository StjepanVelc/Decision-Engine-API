from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate
from app.services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(data: RuleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new decision rule."""
    service = RuleService(db)
    try:
        return await service.create_rule(data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A rule with the name '{data.name}' already exists.",
        )


@router.get("/", response_model=List[RuleResponse])
async def list_rules(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all rules ordered by priority (highest first)."""
    service = RuleService(db)
    return await service.list_rules(skip=skip, limit=limit)


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single rule by ID."""
    service = RuleService(db)
    rule = await service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: UUID, data: RuleUpdate, db: AsyncSession = Depends(get_db)):
    """Partially update a rule."""
    service = RuleService(db)
    try:
        rule = await service.update_rule(rule_id, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A rule with the name '{data.name}' already exists.",
        )
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(rule_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a rule by ID."""
    service = RuleService(db)
    deleted = await service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
