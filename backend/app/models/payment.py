import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
        Index("ix_payments_transaction_reference", "transaction_reference"),
        Index("ix_payments_normalized_payer", "normalized_payer"),
        Index("ix_payments_payment_date", "payment_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_reference: Mapped[str | None] = mapped_column(String(150), nullable=True)
    payer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_payer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    bank_account: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_batch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("import_batches.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    source_batch: Mapped["ImportBatch | None"] = relationship(back_populates="payments")
    candidates: Mapped[list["ReconciliationCandidate"]] = relationship(back_populates="payment")
    allocations: Mapped[list["ReconciliationAllocation"]] = relationship(back_populates="payment")
