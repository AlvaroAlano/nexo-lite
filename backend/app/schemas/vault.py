from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class VaultMonthDeposit(BaseModel):
    year: int
    month: int
    amount: Decimal


class VaultSummary(BaseModel):
    total_deposited: Decimal
    last_real_balance: Optional[Decimal]
    calculated_yield: Optional[Decimal]  # last_real_balance - total_deposited
    last_reconciled_at: Optional[datetime]
    history: List[VaultMonthDeposit]


class VaultReconcileIn(BaseModel):
    real_balance: Decimal


class VaultReconcileOut(BaseModel):
    id: str
    real_balance: Decimal
    recorded_at: datetime
