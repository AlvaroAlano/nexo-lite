from sqlalchemy import Column, Integer, Numeric, String, Boolean, DateTime, UUID, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ExpenseTemplate(Base):
    __tablename__ = "expense_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="Outros")
    expense_type = Column(String(20), nullable=False, default="fixed")
    responsavel = Column(String(20), nullable=False, default="conjunto")
    base_amount = Column(Numeric(12, 2), nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    installment_total = Column(Integer)
    installment_paid = Column(Integer, nullable=False, default=0)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    rent_items = Column(JSONB, nullable=False, server_default='[]')
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    monthly_expenses = relationship("MonthlyExpense", back_populates="template")


class MonthlyExpense(Base):
    __tablename__ = "monthly_expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id = Column(UUID(as_uuid=True), ForeignKey("monthly_periods.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("expense_templates.id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="Outros")
    expense_type = Column(String(20), nullable=False, default="fixed")
    responsavel = Column(String(20), nullable=False, default="conjunto")
    amount = Column(Numeric(12, 2), nullable=False, default=0)
    is_paid = Column(Boolean, nullable=False, default=False)
    paid_at = Column(DateTime(timezone=True))
    installment_current = Column(Integer)
    installment_total = Column(Integer)
    rent_items = Column(JSONB, nullable=False, server_default='[]')
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_excluded = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    period = relationship("MonthlyPeriod", back_populates="expenses")
    template = relationship("ExpenseTemplate", back_populates="monthly_expenses")
