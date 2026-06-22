from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.models.period import MonthlyPeriod
from app.models.expense import MonthlyExpense
from app.schemas.period import PeriodResponse, PeriodUpdate, PeriodWithExpenses
from app.schemas.expense import ExpenseResponse
from app.services.turnover import run_turnover
from app.services.scheduled import materialize_scheduled
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/periods", tags=["periods"])


async def _fetch_period_with_expenses(db: AsyncSession, period: MonthlyPeriod) -> dict:
    exp_result = await db.execute(
        select(MonthlyExpense)
        .where(MonthlyExpense.period_id == period.id)
        .order_by(MonthlyExpense.display_order, MonthlyExpense.created_at)
    )
    expenses = exp_result.scalars().all()
    return {
        "period": PeriodResponse.model_validate(period),
        "expenses": [ExpenseResponse.model_validate(e) for e in expenses],
    }


@router.get("/current", response_model=PeriodWithExpenses)
async def get_current_period(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Return the open period plus all its expenses. Creates one if none exists."""
    result = await db.execute(
        select(MonthlyPeriod).where(
            MonthlyPeriod.user_id == user_id,
            MonthlyPeriod.status == "open",
        )
    )
    period = result.scalars().first()

    if period is None:
        now = datetime.now(timezone.utc)
        period = MonthlyPeriod(
            user_id=user_id,
            year=now.year,
            month=now.month,
            status="open",
        )
        db.add(period)
        await db.flush()
        # Mês recém-criado → traz agendadas que tinham este mês como alvo
        await materialize_scheduled(db, user_id, period)

    return await _fetch_period_with_expenses(db, period)


@router.get("/history")
async def get_periods_history(
    limit: int = 12,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Últimos N meses com free_cash e carryover calculados — alimenta gráficos de stats."""
    result = await db.execute(
        select(
            MonthlyPeriod,
            func.coalesce(func.sum(MonthlyExpense.amount), 0).label("total_expenses"),
        )
        .outerjoin(MonthlyExpense, MonthlyExpense.period_id == MonthlyPeriod.id)
        .where(MonthlyPeriod.user_id == user_id)
        .group_by(MonthlyPeriod.id)
        .order_by(MonthlyPeriod.year.desc(), MonthlyPeriod.month.desc())
        .limit(limit)
    )
    rows = result.all()
    
    def get_additional_total(items_json) -> float:
        if not items_json:
            return 0.0
        total = 0.0
        for item in items_json:
            try:
                total += float(item.get("amount", 0))
            except Exception:
                pass
        return total

    return [
        {
            "year":              p.year,
            "month":             p.month,
            "carryover_balance": float(p.carryover_balance or 0),
            "total_expenses":    float(total_expenses),
            "free_cash":         max(0.0, float(p.income_alvaro or 0) + float(p.income_alexandra or 0) + float(p.carryover_balance or 0) + get_additional_total(p.additional_income_items) - float(total_expenses)),
        }
        for p, total_expenses in reversed(rows)
    ]


@router.get("/{year}/{month}", response_model=PeriodWithExpenses)
async def get_period_by_month(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Return a specific month's period. Used for month navigation.
    Returns 404 if the period doesn't exist (e.g., future month not yet created).
    """
    if not (1 <= month <= 12):
        raise HTTPException(status_code=422, detail="month must be between 1 and 12")
    result = await db.execute(
        select(MonthlyPeriod).where(
            MonthlyPeriod.user_id == user_id,
            MonthlyPeriod.year == year,
            MonthlyPeriod.month == month,
        )
    )
    period = result.scalars().first()
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")

    return await _fetch_period_with_expenses(db, period)


@router.patch("/{period_id}/income", response_model=PeriodResponse)
async def update_income(
    period_id: UUID,
    payload: PeriodUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(MonthlyPeriod).where(
            MonthlyPeriod.id == period_id,
            MonthlyPeriod.user_id == user_id
        )
    )
    period = result.scalars().first()
    if period is None:
        raise HTTPException(status_code=404, detail="Period not found")
    if period.status != "open":
        raise HTTPException(status_code=400, detail="Cannot update income of a closed period")

    if payload.income_alvaro is not None:
        period.income_alvaro = payload.income_alvaro
    if payload.income_alexandra is not None:
        period.income_alexandra = payload.income_alexandra
    if payload.carryover_balance is not None:
        period.carryover_balance = payload.carryover_balance
    if payload.additional_income_items is not None:
        period.additional_income_items = payload.additional_income_items
    if payload.income is not None and payload.income_alvaro is None and payload.income_alexandra is None:
        period.income = payload.income

    return PeriodResponse.model_validate(period)


@router.post("/turnover", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
async def month_turnover(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Close current open period, roll carryover, open next month.
    Only callable when a period is open (RN-06).
    """
    open_check = await db.execute(
        select(MonthlyPeriod).where(
            MonthlyPeriod.user_id == user_id,
            MonthlyPeriod.status == "open",
        )
    )
    if open_check.scalars().first() is None:
        raise HTTPException(status_code=400, detail="No open period to close")
    new_period = await run_turnover(db, user_id)
    return PeriodResponse.model_validate(new_period)
