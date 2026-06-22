from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from collections import defaultdict
from uuid import UUID

from app.database import get_db
from app.models.expense import MonthlyExpense
from app.models.period import MonthlyPeriod
from app.models.vault import VaultReconciliation
from app.schemas.vault import VaultSummary, VaultMonthDeposit, VaultReconcileIn, VaultReconcileOut
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/vault", tags=["vault"])

VAULT_CATEGORY = "Caixinha"


def _safe(v) -> Decimal:
    try:
        return Decimal(str(v)) if v is not None else Decimal("0.00")
    except Exception:
        return Decimal("0.00")


@router.get("/summary", response_model=VaultSummary)
async def get_vault_summary(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    # All paid Caixinha expenses for this user across all periods
    result = await db.execute(
        select(MonthlyExpense, MonthlyPeriod)
        .join(MonthlyPeriod, MonthlyExpense.period_id == MonthlyPeriod.id)
        .where(
            MonthlyPeriod.user_id == user_id,
            MonthlyExpense.category == VAULT_CATEGORY,
            MonthlyExpense.is_paid == True,
        )
        .order_by(MonthlyPeriod.year, MonthlyPeriod.month)
    )
    rows = result.all()

    total_deposited = Decimal("0.00")
    month_totals: dict[tuple, Decimal] = defaultdict(Decimal)
    for expense, period in rows:
        amt = _safe(expense.amount)
        total_deposited += amt
        month_totals[(period.year, period.month)] += amt

    history = [
        VaultMonthDeposit(year=y, month=m, amount=amt)
        for (y, m), amt in sorted(month_totals.items())
    ]

    # Latest reconciliation
    rec_result = await db.execute(
        select(VaultReconciliation)
        .where(VaultReconciliation.user_id == user_id)
        .order_by(VaultReconciliation.recorded_at.desc())
        .limit(1)
    )
    latest = rec_result.scalars().first()

    last_real_balance = _safe(latest.real_balance) if latest else None
    calculated_yield = (last_real_balance - total_deposited) if last_real_balance is not None else None

    return VaultSummary(
        total_deposited=total_deposited,
        last_real_balance=last_real_balance,
        calculated_yield=calculated_yield,
        last_reconciled_at=latest.recorded_at if latest else None,
        history=history,
    )


@router.post("/reconcile", response_model=VaultReconcileOut, status_code=201)
async def reconcile_vault(
    payload: VaultReconcileIn,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    rec = VaultReconciliation(
        user_id=user_id,
        real_balance=payload.real_balance,
    )
    db.add(rec)
    await db.flush()
    return VaultReconcileOut(
        id=str(rec.id),
        real_balance=rec.real_balance,
        recorded_at=rec.recorded_at,
    )
