from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.debt import Debt, DebtPayment
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse, DebtPaymentCreate, DebtPaymentResponse
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/debts", tags=["debts"])


@router.get("/", response_model=List[DebtResponse])
async def list_debts(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt)
        .where(Debt.user_id == user_id)
        .order_by(Debt.display_order, Debt.created_at)
    )
    return [DebtResponse.model_validate(d) for d in result.scalars().all()]


@router.post("/", response_model=DebtResponse, status_code=201)
async def create_debt(
    payload: DebtCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    original = payload.original_amount if payload.original_amount is not None else payload.estimated_amount
    debt = Debt(
        user_id=user_id,
        name=payload.name,
        direction=payload.direction,
        estimated_amount=payload.estimated_amount,
        original_amount=original,
        interest_rate=payload.interest_rate,
        loan_date=payload.loan_date,
        due_date=payload.due_date,
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
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt).where(
            Debt.id == debt_id,
            Debt.user_id == user_id
        )
    )
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")

    if payload.name is not None:
        debt.name = payload.name
    if payload.direction is not None:
        debt.direction = payload.direction
    if payload.estimated_amount is not None:
        debt.estimated_amount = payload.estimated_amount
    if payload.original_amount is not None:
        debt.original_amount = payload.original_amount
    if payload.interest_rate is not None:
        debt.interest_rate = payload.interest_rate
    if payload.loan_date is not None:
        debt.loan_date = payload.loan_date
    if payload.due_date is not None:
        debt.due_date = payload.due_date
    if payload.status is not None:
        debt.status = payload.status
    if payload.display_order is not None:
        debt.display_order = payload.display_order

    return DebtResponse.model_validate(debt)


@router.patch("/{debt_id}/settle", response_model=DebtResponse)
async def settle_debt(
    debt_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt).where(
            Debt.id == debt_id,
            Debt.user_id == user_id
        )
    )
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")
    debt.status = "quitado"
    return DebtResponse.model_validate(debt)


@router.post("/{debt_id}/payments", response_model=DebtPaymentResponse, status_code=201)
async def add_payment(
    debt_id: UUID,
    payload: DebtPaymentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt).where(
            Debt.id == debt_id,
            Debt.user_id == user_id
        )
    )
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")

    payment = DebtPayment(
        debt_id=debt_id,
        amount=payload.amount,
        notes=payload.notes,
        paid_at=payload.paid_at or datetime.now(timezone.utc),
    )
    db.add(payment)

    new_remaining = max(Decimal("0"), Decimal(str(debt.estimated_amount)) - Decimal(str(payload.amount)))
    debt.estimated_amount = new_remaining
    if new_remaining == Decimal("0"):
        debt.status = "quitado"

    await db.flush()
    return DebtPaymentResponse.model_validate(payment)


@router.get("/{debt_id}/payments", response_model=List[DebtPaymentResponse])
async def list_payments(
    debt_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt).where(
            Debt.id == debt_id,
            Debt.user_id == user_id
        )
    )
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")

    payments_result = await db.execute(
        select(DebtPayment)
        .where(DebtPayment.debt_id == debt_id)
        .order_by(DebtPayment.paid_at.desc())
    )
    return [DebtPaymentResponse.model_validate(p) for p in payments_result.scalars().all()]


@router.delete("/{debt_id}", status_code=204)
async def delete_debt(
    debt_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(Debt).where(
            Debt.id == debt_id,
            Debt.user_id == user_id
        )
    )
    debt = result.scalars().first()
    if debt is None:
        raise HTTPException(status_code=404, detail="Debt not found")
    await db.delete(debt)
    await db.flush()
