from pydantic import BaseModel, field_validator, computed_field
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
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

    @field_validator("income", "income_alvaro", "income_alexandra", mode="before")
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
    carryover_balance: Decimal
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def income_total(self) -> Decimal:
        return self.income_alvaro + self.income_alexandra

    model_config = {"from_attributes": True}


class PeriodWithExpenses(BaseModel):
    period: "PeriodResponse"
    expenses: list["ExpenseResponse"]

    model_config = {"from_attributes": True}
