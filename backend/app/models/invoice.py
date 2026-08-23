import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint("total_amount >= 0", name="ck_invoices_total_amount_nonnegative"),
        UniqueConstraint("invoice_number", "currency", name="uq_invoices_number_currency"),
        Index("ix_invoices_invoice_number", "invoice_number"),
        Index("ix_invoices_normalized_customer", "normalized_customer"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_due_date", "due_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_customer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    source_batch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("import_batches.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    source_batch: Mapped["ImportBatch | None"] = relationship(back_populates="invoices")
    candidates: Mapped[list["ReconciliationCandidate"]] = relationship(back_populates="invoice")
    allocations: Mapped[list["ReconciliationAllocation"]] = relationship(back_populates="invoice")
