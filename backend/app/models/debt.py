from sqlalchemy import Column, Integer, Numeric, String, Text, DateTime, UUID, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Debt(Base):
    __tablename__ = "debts"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id          = Column(UUID(as_uuid=True), nullable=False)
    name             = Column(String(255), nullable=False)
    direction        = Column(String(20), nullable=False, default="eu_devo")
    estimated_amount = Column(Numeric(12, 2), nullable=False, default=0)
    original_amount  = Column(Numeric(12, 2))
    interest_rate    = Column(Numeric(6, 2), nullable=False, default=0)  # % ao mês
    status           = Column(String(20), nullable=False, default="ativo")
    loan_date        = Column(Date)
    due_date         = Column(Date)
    display_order    = Column(Integer, nullable=False, default=0)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    payments = relationship(
        "DebtPayment", back_populates="debt", cascade="all, delete-orphan",
        order_by="DebtPayment.paid_at.desc()"
    )


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debt_id    = Column(UUID(as_uuid=True), ForeignKey("debts.id", ondelete="CASCADE"), nullable=False)
    amount     = Column(Numeric(12, 2), nullable=False)
    notes      = Column(Text)
    paid_at    = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    debt = relationship("Debt", back_populates="payments")
