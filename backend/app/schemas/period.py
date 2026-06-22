from pydantic import BaseModel, field_validator, computed_field
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.schemas.expense import ExpenseResponse


def safe_decimal(v) -> Decimal:
    """Convert any value to Decimal safely, defaulting to 0.00."""
    if v is None:
        return Decimal("0.00")
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0.00")


class PeriodCreate(BaseModel):
    year: int
    month: int
    income_alvaro: Decimal = Decimal("0.00")
    income_alexandra: Decimal = Decimal("0.00")

    @field_validator("income_alvaro", "income_alexandra", mode="before")
    @classmethod
    def validate_incomes(cls, v):
        return safe_decimal(v)


class PeriodUpdate(BaseModel):
    income: Optional[Decimal] = None          # legacy single-field update
    income_alvaro: Optional[Decimal] = None
    income_alexandra: Optional[Decimal] = None
    carryover_balance: Optional[Decimal] = None
    additional_income_items: Optional[list[dict]] = None

    @field_validator("income", "income_alvaro", "income_alexandra", "carryover_balance", mode="before")
    @classmethod
    def validate_incomes(cls, v):
        if v is None:
            return v
        return safe_decimal(v)


class PeriodResponse(BaseModel):
    id: UUID
    user_id: UUID
    year: int
    month: int
    status: str
    income: Decimal
    income_alvaro: Decimal
    income_alexandra: Decimal
    additional_income_items: list[dict] = []
    carryover_balance: Decimal
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def additional_income_total(self) -> Decimal:
        items = self.additional_income_items or []
        total = Decimal("0.00")
        for item in items:
            try:
                total += Decimal(str(item.get("amount", 0)))
            except Exception:
                pass
        return total

    @computed_field
    @property
    def income_total(self) -> Decimal:
        return self.income_alvaro + self.income_alexandra + self.additional_income_total

    model_config = {"from_attributes": True}


class PeriodWithExpenses(BaseModel):
    period: PeriodResponse
    expenses: list[ExpenseResponse]

    model_config = {"from_attributes": True}
