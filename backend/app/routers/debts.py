from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.database import get_db
from app.models.debt import Debt
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse
from app.config import settings

router = APIRouter(prefix="/debts", tags=["debts"])


def get_user_id() -> UUID:
    return settings.DEMO_USER_ID


@router.get("/", response_model=List[DebtResponse])
async def list_debts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Debt)
        .where(Debt.user_id == get_user_id())
        .order_by(Debt.display_order, Debt.created_at)
    )
    return [DebtResponse.model_validate(d) for d in result.scalars().all()]


@router.post("/", response_model=DebtResponse, status_code=201)
async def create_debt(payload: DebtCreate, db: AsyncSession = Depends(get_db)):
    debt = Debt(
        user_id=get_user_id(),
        name=payload.name,
        estimated_amount=payload.estimated_amount,
        display_order=payload.display_order,
    )
    db.add(debt)
    await db.flush()
    return DebtResponse.model_validate(debt)


@router.patch("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: UUID,
    payload: DebtUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Debt).where(Debt.id == debt_id))
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")

    if payload.name is not None:
        debt.name = payload.name
    if payload.estimated_amount is not None:
        debt.estimated_amount = payload.estimated_amount
    if payload.display_order is not None:
        debt.display_order = payload.display_order

    return DebtResponse.model_validate(debt)


@router.delete("/{debt_id}", status_code=204)
async def delete_debt(debt_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Debt).where(Debt.id == debt_id))
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")
    await db.delete(debt)
    await db.flush()
