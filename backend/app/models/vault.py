from sqlalchemy import Column, Numeric, DateTime, UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class VaultReconciliation(Base):
    __tablename__ = "vault_reconciliations"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), nullable=False)
    real_balance = Column(Numeric(12, 2), nullable=False)
    recorded_at  = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
