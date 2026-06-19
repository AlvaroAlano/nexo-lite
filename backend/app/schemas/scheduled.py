from pydantic import BaseModel, field_validator
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal

from app.schemas.expense import safe_decimal, ExpenseType, Responsavel


class ScheduledCreate(BaseModel):
    target_year: int
    target_month: int
    name: str
    category: str = "Outros"
    category_id: Optional[UUID] = None
    expense_type: ExpenseType = "variable"
    responsavel: Responsavel = "conjunto"
    amount: Decimal = Decimal("0.00")
    is_paid: bool = False
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None
    display_order: int = 0

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        return safe_decimal(v)

    @field_validator("target_month")
    @classmethod
    def validate_month(cls, v):
        if not (1 <= v <= 12):
            raise ValueError("target_month must be between 1 and 12")
        return v


class ScheduledResponse(BaseModel):
    id: UUID
    user_id: UUID
    target_year: int
    target_month: int
    name: str
    category: str
    category_id: Optional[UUID] = None
    expense_type: str
    responsavel: str
    amount: Decimal
    is_paid: bool
    installment_current: Optional[int]
    installment_total: Optional[int]
    display_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
