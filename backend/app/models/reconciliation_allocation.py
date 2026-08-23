import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReconciliationAllocation(Base):
    __tablename__ = "reconciliation_allocations"
    __table_args__ = (
        CheckConstraint("allocated_amount > 0", name="ck_allocations_amount_positive"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name="ck_allocations_confidence_score_range"),
        Index("ix_allocations_payment_id", "payment_id"),
        Index("ix_allocations_invoice_id", "invoice_id"),
        Index("ix_allocations_run_id", "run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reconciliation_runs.id"), nullable=False)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"), nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped["ReconciliationRun"] = relationship(back_populates="allocations")
    payment: Mapped["Payment"] = relationship(back_populates="allocations")
    invoice: Mapped["Invoice"] = relationship(back_populates="allocations")
    created_by_user: Mapped["User | None"] = relationship(back_populates="allocations")
