from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.services.decision_service import DecisionService
from app.repositories.decision_repository import DecisionRepository

router = APIRouter(prefix="/decisions", tags=["Decisions"])


@router.post("/evaluate", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def evaluate_decision(
    request: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluate a JSON payload against all active rules and return a decision.

    - **APPROVE** – no rules triggered
    - **REVIEW**  – at least one REVIEW rule triggered, no REJECT rules
    - **REJECT**  – at least one REJECT rule triggered
    """
    service = DecisionService(db)
    return await service.evaluate(request, category=request.category)


@router.get("/", response_model=List[DecisionResponse])
async def list_decisions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all past decisions (newest first)."""
    repo = DecisionRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.get("/reference/{reference_id}", response_model=List[DecisionResponse])
async def decisions_by_reference(
    reference_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all decisions for a given external reference ID (e.g. transaction ID)."""
    repo = DecisionRepository(db)
    results = await repo.get_by_reference(reference_id)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No decisions found for reference '{reference_id}'",
        )
    return results


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(decision_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single decision by its ID."""
    repo = DecisionRepository(db)
    decision = await repo.get_by_id(decision_id)
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    return decision
