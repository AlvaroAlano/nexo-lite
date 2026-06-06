from pydantic import BaseModel, field_validator
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


def safe_decimal(v) -> Decimal:
    if v is None:
        return Decimal("0.00")
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0.00")


ExpenseType = Literal["fixed", "variable", "installment", "rent"]
Responsavel = Literal["alvaro", "alexandra", "conjunto"]
RentItemType = Literal["fixed", "variable", "installment"]


class RentItem(BaseModel):
    id: str
    name: str
    amount: Decimal = Decimal("0.00")
    type: RentItemType = "fixed"
    installment_current: Optional[int] = None
    installment_total: Optional[int] = None

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        return safe_decimal(v)


# ─── Template schemas ────────────────────────────────────────────────────────

class TemplateCreate(BaseModel):
    name: str
    category: str = "Outros"
    category_id: Optional[UUID] = None
    expense_type: ExpenseType = "fixed"
    responsavel: Responsavel = "conjunto"
    base_amount: Decimal = Decimal("0.00")
    installment_total: Optional[int] = None
    display_order: int = 0
    rent_items: list[dict] = []

    @field_validator("base_amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        return safe_decimal(v)


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None
    expense_type: Optional[ExpenseType] = None
    responsavel: Optional[Responsavel] = None
    base_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None
    installment_total: Optional[int] = None
    installment_paid: Optional[int] = None
    display_order: Optional[int] = None
    rent_items: Optional[list[dict]] = None

    @field_validator("base_amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        if v is None:
            return v
        return safe_decimal(v)


class TemplateResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    category: str
    category_id: Optional[UUID] = None
    expense_type: str
    responsavel: str
    base_amount: Decimal
    is_active: bool
    installment_total: Optional[int]
    installment_paid: int
    display_order: int
    created_at: datetime
    rent_items: list[dict] = []

    model_config = {"from_attributes": True}


# ─── Monthly expense schemas ─────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
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
    rent_items: list[dict] = []

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        return safe_decimal(v)


class ExpenseUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[UUID] = None
    responsavel: Optional[Responsavel] = None
    amount: Optional[Decimal] = None
    is_paid: Optional[bool] = None

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v):
        if v is None:
            return v
        return safe_decimal(v)


class RentUpdate(BaseModel):
    rent_items: list[RentItem] = []


class ExpenseResponse(BaseModel):
    id: UUID
    period_id: UUID
    template_id: Optional[UUID]
    name: str
    category: str
    category_id: Optional[UUID] = None
    expense_type: str
    responsavel: str
    amount: Decimal
    is_paid: bool
    paid_at: Optional[datetime]
    installment_current: Optional[int]
    installment_total: Optional[int]
    rent_base: Decimal    # legacy
    rent_water: Decimal   # legacy
    rent_gas: Decimal     # legacy
    rent_extras: Decimal  # legacy
    rent_items: list[dict] = []
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
