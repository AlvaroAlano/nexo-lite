from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    color: str = "slate"
    icon: str = "Package"
    display_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None


class CategoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    color: str
    icon: str
    display_order: int
    created_at: datetime

    model_config = {"from_attributes": True}
