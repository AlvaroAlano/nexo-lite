from sqlalchemy import Column, Integer, Numeric, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ScheduledExpense(Base):
    __tablename__ = "scheduled_expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    target_year = Column(Integer, nullable=False)
    target_month = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="Outros")
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    expense_type = Column(String(20), nullable=False, default="variable")
    responsavel = Column(String(20), nullable=False, default="conjunto")
    amount = Column(Numeric(12, 2), nullable=False, default=0)
    is_paid = Column(Boolean, nullable=False, default=False)
    installment_current = Column(Integer)
    installment_total = Column(Integer)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
