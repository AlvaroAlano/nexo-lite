from sqlalchemy import Column, Integer, Numeric, String, DateTime, UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Debt(Base):
    __tablename__ = "debts"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), nullable=False)
    name             = Column(String(255), nullable=False)
    estimated_amount = Column(Numeric(12, 2), nullable=False, default=0)
    display_order    = Column(Integer, nullable=False, default=0)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
