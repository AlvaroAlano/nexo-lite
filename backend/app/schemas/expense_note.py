from pydantic import BaseModel
from datetime import datetime
import uuid


class ExpenseNoteCreate(BaseModel):
    body: str
    created_by: str = "Usuário"


class ExpenseNoteResponse(BaseModel):
    id: uuid.UUID
    expense_id: uuid.UUID
    body: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
