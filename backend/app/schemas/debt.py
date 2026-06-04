from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional
import uuid


class DebtCreate(BaseModel):
    name: str
    estimated_amount: Decimal = Decimal("0.00")
    display_order: int = 0


class DebtUpdate(BaseModel):
    name: Optional[str] = None
    estimated_amount: Optional[Decimal] = None
    display_order: Optional[int] = None


class DebtResponse(BaseModel):
    id: uuid.UUID
    name: str
    estimated_amount: Decimal
    display_order: int
    updated_at: datetime

    model_config = {"from_attributes": True}
