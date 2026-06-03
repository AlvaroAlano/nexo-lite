from pydantic import BaseModel
from decimal import Decimal
from typing import List


class CategorySummary(BaseModel):
    category: str
    total: Decimal
    paid: Decimal
    count: int


class PersonSummary(BaseModel):
    responsavel: str
    income: Decimal
    total_committed: Decimal
    saldo: Decimal


class DashboardSummary(BaseModel):
    # Totals
    income_alvaro: Decimal
    income_alexandra: Decimal
    income_total: Decimal
    carryover_balance: Decimal
    total_committed: Decimal
    total_paid: Decimal
    free_cash: Decimal
    paid_count: int
    total_count: int
    # Per-person breakdown
    saldo_alvaro: Decimal
    saldo_alexandra: Decimal
    # Category breakdown
    categories: List[CategorySummary]
