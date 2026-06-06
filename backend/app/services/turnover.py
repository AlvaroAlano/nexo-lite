"""
Turnover Service — Month closing engine.

Responsibilities:
  1. Close current open period
  2. Compute carryover: (income + carryover_prev) - Σ(expenses)
  3. Open next month period
  4. Clone active templates as monthly expenses:
     - fixed/variable → clone with base_amount
     - rent            → clone with rent_base pre-filled, amount = 0 (user fills during check-in)
     - installment     → clone only if installment_paid < installment_total; increment counter
"""

from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.period import MonthlyPeriod
from app.models.expense import ExpenseTemplate, MonthlyExpense


def _next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def _safe_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0.00")


async def run_turnover(db: AsyncSession, user_id: UUID) -> MonthlyPeriod:
    # ── 1. Find the current open period ──────────────────────────────────────
    result = await db.execute(
        select(MonthlyPeriod).where(
            MonthlyPeriod.user_id == user_id,
            MonthlyPeriod.status == "open",
        )
    )
    current = result.scalars().first()

    if current is None:
        # No open period — create one for the current calendar month
        now = datetime.now(timezone.utc)
        current = MonthlyPeriod(
            user_id=user_id,
            year=now.year,
            month=now.month,
            status="open",
            income=Decimal("0.00"),
            carryover_balance=Decimal("0.00"),
        )
        db.add(current)
        await db.flush()

    # ── 2. Load expenses for current period ──────────────────────────────────
    exp_result = await db.execute(
        select(MonthlyExpense).where(MonthlyExpense.period_id == current.id)
    )
    current_expenses = exp_result.scalars().all()

    total_expenses = sum(_safe_decimal(e.amount) for e in current_expenses)
    income = _safe_decimal(current.income_alvaro) + _safe_decimal(current.income_alexandra)
    prev_carryover = _safe_decimal(current.carryover_balance)

    # Carryover: available budget minus what was committed (not just paid)
    carryover = income + prev_carryover - total_expenses
    # Floor at 0 — we don't propagate debt between months
    carryover = max(Decimal("0.00"), carryover)

    # ── 3. Close current period ───────────────────────────────────────────────
    current.status = "closed"

    # ── 4. Create next period ─────────────────────────────────────────────────
    next_year, next_month = _next_month(current.year, current.month)

    new_period = MonthlyPeriod(
        user_id=user_id,
        year=next_year,
        month=next_month,
        status="open",
        income=Decimal("0.00"),
        carryover_balance=carryover,
    )
    db.add(new_period)
    await db.flush()

    # ── 5. Clone active templates ─────────────────────────────────────────────
    tmpl_result = await db.execute(
        select(ExpenseTemplate).where(
            ExpenseTemplate.user_id == user_id,
            ExpenseTemplate.is_active == True,
        ).order_by(ExpenseTemplate.display_order)
    )
    templates = tmpl_result.scalars().all()

    for tmpl in templates:
        resp = getattr(tmpl, "responsavel", "conjunto") or "conjunto"

        if tmpl.expense_type == "installment":
            paid = tmpl.installment_paid or 0
            total = tmpl.installment_total or 1
            if paid >= total:
                continue  # installment fully paid — skip (RN-09)
            tmpl.installment_paid = paid + 1
            expense = MonthlyExpense(
                period_id=new_period.id,
                template_id=tmpl.id,
                name=tmpl.name,
                category=tmpl.category,
                category_id=tmpl.category_id,
                expense_type="installment",
                responsavel=resp,
                amount=_safe_decimal(tmpl.base_amount),
                installment_current=tmpl.installment_paid,
                installment_total=total,
                display_order=tmpl.display_order,
            )
        elif tmpl.expense_type == "rent":
            tmpl_items = list(getattr(tmpl, "rent_items", None) or [])
            cloned_items: list[dict] = []
            updated_tmpl_items: list[dict] = []

            for item in tmpl_items:
                item_type = item.get("type", "fixed")
                if item_type == "installment":
                    current = int(item.get("installment_current") or 0)
                    total_inst = int(item.get("installment_total") or 0)
                    if total_inst > 0 and current > total_inst:
                        # Completed — keep in template, skip clone
                        updated_tmpl_items.append(item)
                        continue
                    cloned_items.append({**item, "installment_current": current})
                    updated_tmpl_items.append({**item, "installment_current": current + 1})
                elif item_type == "variable":
                    # Reset to 0 each month — user fills in during check-in
                    cloned_items.append({**item, "amount": "0.00"})
                    updated_tmpl_items.append(item)
                else:  # fixed
                    cloned_items.append(item)
                    updated_tmpl_items.append(item)

            tmpl.rent_items = updated_tmpl_items
            total = sum(_safe_decimal(i.get("amount", 0)) for i in cloned_items)
            expense = MonthlyExpense(
                period_id=new_period.id,
                template_id=tmpl.id,
                name=tmpl.name,
                category=tmpl.category,
                category_id=tmpl.category_id,
                expense_type="rent",
                responsavel=resp,
                amount=total,
                rent_items=cloned_items,
                display_order=tmpl.display_order,
            )
        else:  # fixed or variable
            expense = MonthlyExpense(
                period_id=new_period.id,
                template_id=tmpl.id,
                name=tmpl.name,
                category=tmpl.category,
                category_id=tmpl.category_id,
                responsavel=resp,
                expense_type=tmpl.expense_type,
                amount=_safe_decimal(tmpl.base_amount),
                display_order=tmpl.display_order,
            )
        db.add(expense)

    # Always ensure Caixinha exists in the new period (independent of templates)
    caixinha_created = any(
        getattr(tmpl, "category", "") == "Caixinha" for tmpl in templates
    )
    if not caixinha_created:
        db.add(MonthlyExpense(
            period_id=new_period.id,
            name="Caixinha",
            category="Caixinha",
            expense_type="variable",
            amount=Decimal("0.00"),
            display_order=999,
        ))

    await db.flush()
    return new_period
