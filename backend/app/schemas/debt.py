from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
import uuid


class DebtPaymentCreate(BaseModel):
    amount: Decimal
    notes: Optional[str] = None
    paid_at: Optional[datetime] = None


class DebtPaymentResponse(BaseModel):
    id: uuid.UUID
    debt_id: uuid.UUID
    amount: Decimal
    notes: Optional[str]
    paid_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DebtCreate(BaseModel):
    name: str
    direction: str = "eu_devo"
    estimated_amount: Decimal = Decimal("0.00")
    original_amount: Optional[Decimal] = None
    loan_date: Optional[date] = None
    due_date: Optional[date] = None
    display_order: int = 0


class DebtUpdate(BaseModel):
    name: Optional[str] = None
    direction: Optional[str] = None
    estimated_amount: Optional[Decimal] = None
    original_amount: Optional[Decimal] = None
    loan_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    display_order: Optional[int] = None


class DebtResponse(BaseModel):
    id: uuid.UUID
    name: str
    direction: str
    estimated_amount: Decimal
    original_amount: Optional[Decimal]
    status: str
    loan_date: Optional[date]
    due_date: Optional[date]
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
