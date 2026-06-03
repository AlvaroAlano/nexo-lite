from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from decimal import Decimal
from collections import defaultdict

from app.database import get_db
from app.models.period import MonthlyPeriod
from app.models.expense import MonthlyExpense
from app.schemas.summary import DashboardSummary, CategorySummary

router = APIRouter(prefix="/summary", tags=["summary"])


def _safe(v) -> Decimal:
    if v is None:
        return Decimal("0.00")
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0.00")


@router.get("/{period_id}", response_model=DashboardSummary)
async def get_summary(period_id: UUID, db: AsyncSession = Depends(get_db)):
    p_result = await db.execute(select(MonthlyPeriod).where(MonthlyPeriod.id == period_id))
    period = p_result.scalars().first()
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")

    e_result = await db.execute(
        select(MonthlyExpense).where(MonthlyExpense.period_id == period_id)
    )
    expenses = e_result.scalars().all()

    income_alvaro = _safe(period.income_alvaro)
    income_alexandra = _safe(period.income_alexandra)
    income_total = income_alvaro + income_alexandra
    carryover = _safe(period.carryover_balance)

    total_committed = sum(_safe(e.amount) for e in expenses)
    total_paid = sum(_safe(e.amount) for e in expenses if e.is_paid)
    free_cash = income_total + carryover - total_committed

    # Per-person saldo (individual expenses only; 'conjunto' goes to total only)
    alvaro_expenses = sum(_safe(e.amount) for e in expenses if e.responsavel == "alvaro")
    alexandra_expenses = sum(_safe(e.amount) for e in expenses if e.responsavel == "alexandra")
    saldo_alvaro = income_alvaro - alvaro_expenses
    saldo_alexandra = income_alexandra - alexandra_expenses

    # Category breakdown
    cat_totals: dict[str, dict] = defaultdict(lambda: {"total": Decimal("0"), "paid": Decimal("0"), "count": 0})
    for e in expenses:
        cat = e.category or "Outros"
        cat_totals[cat]["total"] += _safe(e.amount)
        cat_totals[cat]["count"] += 1
        if e.is_paid:
            cat_totals[cat]["paid"] += _safe(e.amount)

    categories = [
        CategorySummary(category=cat, **data)
        for cat, data in sorted(cat_totals.items())
    ]

    return DashboardSummary(
        income_alvaro=income_alvaro,
        income_alexandra=income_alexandra,
        income_total=income_total,
        carryover_balance=carryover,
        total_committed=total_committed,
        total_paid=total_paid,
        free_cash=free_cash,
        paid_count=sum(1 for e in expenses if e.is_paid),
        total_count=len(expenses),
        saldo_alvaro=saldo_alvaro,
        saldo_alexandra=saldo_alexandra,
        categories=categories,
    )
