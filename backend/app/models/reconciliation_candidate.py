import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReconciliationCandidate(Base):
    __tablename__ = "reconciliation_candidates"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_candidates_score_range"),
        CheckConstraint("amount_score >= 0 AND amount_score <= 100", name="ck_candidates_amount_score_range"),
        CheckConstraint("customer_score >= 0 AND customer_score <= 100", name="ck_candidates_customer_score_range"),
        CheckConstraint("reference_score >= 0 AND reference_score <= 100", name="ck_candidates_reference_score_range"),
        CheckConstraint("date_score >= 0 AND date_score <= 100", name="ck_candidates_date_score_range"),
        CheckConstraint("currency_score >= 0 AND currency_score <= 100", name="ck_candidates_currency_score_range"),
        CheckConstraint("history_score >= 0 AND history_score <= 100", name="ck_candidates_history_score_range"),
        CheckConstraint("score_gap >= 0 AND score_gap <= 100", name="ck_candidates_score_gap_range"),
        Index("ix_candidates_payment_id", "payment_id"),
        Index("ix_candidates_invoice_id", "invoice_id"),
        Index("ix_candidates_run_id", "run_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reconciliation_runs.id"), nullable=False)
    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id"), nullable=False)
    invoice_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    decision: Mapped[str | None] = mapped_column(String(30), nullable=True)
    amount_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    customer_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    reference_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    date_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    currency_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    history_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    score_gap: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    explanation: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped["ReconciliationRun"] = relationship(back_populates="candidates")
    payment: Mapped["Payment"] = relationship(back_populates="candidates")
    invoice: Mapped["Invoice"] = relationship(back_populates="candidates")
