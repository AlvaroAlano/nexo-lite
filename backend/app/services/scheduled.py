"""Materializa despesas agendadas no período do mês alvo, quando ele é criado."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.scheduled_expense import ScheduledExpense
from app.models.expense import MonthlyExpense
from app.models.period import MonthlyPeriod


async def materialize_scheduled(db: AsyncSession, user_id: UUID, period: MonthlyPeriod) -> None:
    """Move agendadas com alvo == (period.year, period.month) para monthly_expenses."""
    result = await db.execute(
        select(ScheduledExpense)
        .where(
            ScheduledExpense.user_id == user_id,
            ScheduledExpense.target_year == period.year,
            ScheduledExpense.target_month == period.month,
        )
        .order_by(ScheduledExpense.display_order, ScheduledExpense.created_at)
    )
    scheduled = result.scalars().all()
    if not scheduled:
        return

    existing = await db.execute(
        select(MonthlyExpense).where(MonthlyExpense.period_id == period.id)
    )
    base_order = len(existing.scalars().all())

    for i, s in enumerate(scheduled):
        db.add(MonthlyExpense(
            period_id=period.id,
            name=s.name,
            category=s.category,
            category_id=s.category_id,
            expense_type=s.expense_type,
            responsavel=s.responsavel,
            amount=s.amount,
            is_paid=s.is_paid,
            installment_current=s.installment_current,
            installment_total=s.installment_total,
            display_order=base_order + i,
        ))
        await db.delete(s)

    await db.flush()
