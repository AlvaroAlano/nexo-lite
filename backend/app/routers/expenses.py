from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.expense import MonthlyExpense
from app.models.expense_note import ExpenseNote
from app.models.category import Category
from app.models.period import MonthlyPeriod
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, RentUpdate, ExpenseResponse
from app.schemas.expense_note import ExpenseNoteCreate, ExpenseNoteResponse
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/expenses", tags=["expenses"])


async def _get_owned_expense(db: AsyncSession, expense_id: UUID, user_id: UUID) -> MonthlyExpense:
    """Fetch an expense while enforcing that its parent period belongs to user_id.

    MonthlyExpense has no user_id column of its own — ownership is derived
    through period_id. Returns 404 (not 403) to avoid disclosing that the
    expense exists under another user. Eager-loads `period` so callers can
    check `.period.status` without a second (lazy, async-unsafe) query.
    """
    result = await db.execute(
        select(MonthlyExpense)
        .options(joinedload(MonthlyExpense.period))
        .join(MonthlyPeriod, MonthlyExpense.period_id == MonthlyPeriod.id)
        .where(MonthlyExpense.id == expense_id, MonthlyPeriod.user_id == user_id)
    )
    expense = result.scalars().first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


def _ensure_period_open(expense: MonthlyExpense) -> None:
    """RN-10 — meses fechados são somente leitura."""
    if expense.period.status != "open":
        raise HTTPException(status_code=400, detail="Cannot modify an expense in a closed period")


async def _get_owned_category(db: AsyncSession, category_id: UUID, user_id: UUID) -> Category:
    cat = (
        await db.execute(select(Category).where(Category.id == category_id, Category.user_id == user_id))
    ).scalars().first()
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.post("/{period_id}", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    period_id: UUID,
    payload: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    period = (
        await db.execute(
            select(MonthlyPeriod).where(MonthlyPeriod.id == period_id, MonthlyPeriod.user_id == user_id)
        )
    ).scalars().first()
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.status != "open":
        raise HTTPException(status_code=400, detail="Cannot add expense to a closed period")

    category_name = payload.category
    if payload.category_id is not None:
        cat = await _get_owned_category(db, payload.category_id, user_id)
        category_name = cat.name

    expense = MonthlyExpense(
        period_id=period_id,
        name=payload.name,
        category=category_name,
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
    user_id: UUID = Depends(get_current_user_id),
):
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)

    if payload.name is not None:
        expense.name = payload.name
    if payload.responsavel is not None:
        expense.responsavel = payload.responsavel
    if payload.category_id is not None:
        cat = await _get_owned_category(db, payload.category_id, user_id)
        expense.category_id = payload.category_id
        expense.category = cat.name
    elif payload.category is not None:
        expense.category = payload.category
    if payload.amount is not None:
        if expense.expense_type == "rent":
            raise HTTPException(status_code=400, detail="Use PATCH /expenses/{id}/rent to update rent amount")
        expense.amount = payload.amount
    if payload.is_paid is not None:
        expense.is_paid = payload.is_paid
        expense.paid_at = datetime.now(timezone.utc) if payload.is_paid else None

    new_current = payload.installment_current if payload.installment_current is not None else expense.installment_current
    new_total = payload.installment_total if payload.installment_total is not None else expense.installment_total
    if new_current is not None and new_total is not None and new_current > new_total:
        raise HTTPException(status_code=400, detail="installment_current cannot exceed installment_total")
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
    user_id: UUID = Depends(get_current_user_id),
):
    """Save rent line items and recompute total from their sum."""
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)
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
    user_id: UUID = Depends(get_current_user_id),
):
    """Convenience endpoint for the one-tap 'Pago' button."""
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)

    expense.is_paid = not expense.is_paid
    expense.paid_at = datetime.now(timezone.utc) if expense.is_paid else None

    return ExpenseResponse.model_validate(expense)


@router.patch("/{expense_id}/toggle-excluded", response_model=ExpenseResponse)
async def toggle_excluded(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Convenience endpoint to toggle is_excluded."""
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)

    expense.is_excluded = not expense.is_excluded

    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)
    if expense.name == "Caixinha" or expense.category == "Caixinha":
        raise HTTPException(status_code=403, detail="Caixinha expense cannot be deleted")
    await db.delete(expense)
    await db.flush()


# ── Expense Notes ─────────────────────────────────────────────────────────────

@router.get("/{expense_id}/notes", response_model=List[ExpenseNoteResponse])
async def list_notes(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    await _get_owned_expense(db, expense_id, user_id)
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
    user_id: UUID = Depends(get_current_user_id),
):
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)
    note = ExpenseNote(expense_id=expense_id, body=payload.body, created_by=payload.created_by)
    db.add(note)
    await db.flush()
    return ExpenseNoteResponse.model_validate(note)


@router.delete("/{expense_id}/notes/{note_id}", status_code=204)
async def delete_note(
    expense_id: UUID,
    note_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    expense = await _get_owned_expense(db, expense_id, user_id)
    _ensure_period_open(expense)
    result = await db.execute(
        select(ExpenseNote).where(ExpenseNote.id == note_id, ExpenseNote.expense_id == expense_id)
    )
    note = result.scalars().first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note)
    await db.flush()
