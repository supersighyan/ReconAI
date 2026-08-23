import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"
    __table_args__ = (
        CheckConstraint("invoice_count >= 0", name="ck_runs_invoice_count_nonnegative"),
        CheckConstraint("payment_count >= 0", name="ck_runs_payment_count_nonnegative"),
        CheckConstraint("auto_matched_count >= 0", name="ck_runs_auto_matched_count_nonnegative"),
        CheckConstraint("review_count >= 0", name="ck_runs_review_count_nonnegative"),
        CheckConstraint("unmatched_count >= 0", name="ck_runs_unmatched_count_nonnegative"),
        CheckConstraint("exception_count >= 0", name="ck_runs_exception_count_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    invoice_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    payment_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    auto_matched_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    unmatched_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    exception_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    engine_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    started_by_user: Mapped["User | None"] = relationship(back_populates="reconciliation_runs")
    candidates: Mapped[list["ReconciliationCandidate"]] = relationship(back_populates="run")
    allocations: Mapped[list["ReconciliationAllocation"]] = relationship(back_populates="run")
    exceptions: Mapped[list["ExceptionRecord"]] = relationship(back_populates="run")
