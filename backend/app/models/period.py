from sqlalchemy import Column, Integer, Numeric, String, DateTime, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class MonthlyPeriod(Base):
    __tablename__ = "monthly_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    income = Column(Numeric(12, 2), nullable=False, default=0)           # legacy total — kept for compatibility
    income_alvaro = Column(Numeric(12, 2), nullable=False, default=0)
    income_alexandra = Column(Numeric(12, 2), nullable=False, default=0)
    additional_income_items = Column(JSONB, nullable=False, server_default='[]')
    carryover_balance = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    expenses = relationship("MonthlyExpense", back_populates="period", cascade="all, delete-orphan")
