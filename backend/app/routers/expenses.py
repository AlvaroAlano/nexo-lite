from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.expense import MonthlyExpense
from app.models.expense_note import ExpenseNote
from app.models.category import Category
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, RentUpdate, ExpenseResponse
from app.schemas.expense_note import ExpenseNoteCreate, ExpenseNoteResponse

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/{period_id}", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    period_id: UUID,
    payload: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
):
    expense = MonthlyExpense(
        period_id=period_id,
        name=payload.name,
        category=payload.category,
        category_id=payload.category_id,
        expense_type=payload.expense_type,
        responsavel=payload.responsavel,
        amount=payload.amount,
        is_paid=payload.is_paid,
        paid_at=datetime.now(timezone.utc) if payload.is_paid else None,
        installment_current=payload.installment_current,
        installment_total=payload.installment_total,
        display_order=payload.display_order,
        rent_items=payload.rent_items if payload.expense_type == "rent" else [],
    )
    db.add(expense)
    await db.flush()
    return ExpenseResponse.model_validate(expense)


@router.patch("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: UUID,
    payload: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    if payload.name is not None:
        expense.name = payload.name
    if payload.responsavel is not None:
        expense.responsavel = payload.responsavel
    if payload.category_id is not None:
        expense.category_id = payload.category_id
        cat = (await db.execute(select(Category).where(Category.id == payload.category_id))).scalars().first()
        expense.category = cat.name if cat else expense.category
    elif payload.category is not None:
        expense.category = payload.category
    if payload.amount is not None:
        if expense.expense_type == "rent":
            raise HTTPException(status_code=400, detail="Use PATCH /expenses/{id}/rent to update rent amount")
        expense.amount = payload.amount
    if payload.is_paid is not None:
        expense.is_paid = payload.is_paid
        expense.paid_at = datetime.now(timezone.utc) if payload.is_paid else None
    if payload.installment_current is not None:
        expense.installment_current = payload.installment_current
    if payload.installment_total is not None:
        expense.installment_total = payload.installment_total

    return ExpenseResponse.model_validate(expense)


@router.patch("/{expense_id}/rent", response_model=ExpenseResponse)
async def update_rent(
    expense_id: UUID,
    payload: RentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Save rent line items and recompute total from their sum."""
    result = await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.expense_type != "rent":
        raise HTTPException(status_code=400, detail="Expense is not of type 'rent'")

    items = [item.model_dump() for item in payload.rent_items]
    expense.rent_items = items
    expense.amount = sum(
        Decimal(str(item.get("amount") or 0)) for item in items
    )
    return ExpenseResponse.model_validate(expense)


@router.patch("/{expense_id}/toggle-paid", response_model=ExpenseResponse)
async def toggle_paid(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Convenience endpoint for the one-tap 'Pago' button."""
    result = await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.is_paid = not expense.is_paid
    expense.paid_at = datetime.now(timezone.utc) if expense.is_paid else None

    return ExpenseResponse.model_validate(expense)


@router.patch("/{expense_id}/toggle-excluded", response_model=ExpenseResponse)
async def toggle_excluded(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Convenience endpoint to toggle is_excluded."""
    result = await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.is_excluded = not expense.is_excluded

    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    if expense.name == "Caixinha" or expense.category == "Caixinha":
        raise HTTPException(status_code=403, detail="Caixinha expense cannot be deleted")
    await db.delete(expense)
    await db.flush()


# ── Expense Notes ─────────────────────────────────────────────────────────────

@router.get("/{expense_id}/notes", response_model=List[ExpenseNoteResponse])
async def list_notes(expense_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExpenseNote)
        .where(ExpenseNote.expense_id == expense_id)
        .order_by(ExpenseNote.created_at.desc())
    )
    return [ExpenseNoteResponse.model_validate(n) for n in result.scalars().all()]


@router.post("/{expense_id}/notes", response_model=ExpenseNoteResponse, status_code=201)
async def add_note(
    expense_id: UUID,
    payload: ExpenseNoteCreate,
    db: AsyncSession = Depends(get_db),
):
    expense = (await db.execute(select(MonthlyExpense).where(MonthlyExpense.id == expense_id))).scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    note = ExpenseNote(expense_id=expense_id, body=payload.body, created_by=payload.created_by)
    db.add(note)
    await db.flush()
    return ExpenseNoteResponse.model_validate(note)


@router.delete("/{expense_id}/notes/{note_id}", status_code=204)
async def delete_note(expense_id: UUID, note_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExpenseNote).where(ExpenseNote.id == note_id, ExpenseNote.expense_id == expense_id)
    )
    note = result.scalars().first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.flush()
