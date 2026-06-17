from sqlalchemy import Column, String, Text, DateTime, UUID, ForeignKey
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ExpenseNote(Base):
    __tablename__ = "expense_notes"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("monthly_expenses.id", ondelete="CASCADE"), nullable=False)
    body       = Column(Text, nullable=False)
    created_by = Column(String(100), nullable=False, default="Usuário")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
