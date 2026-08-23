import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    import_batches: Mapped[list["ImportBatch"]] = relationship(back_populates="uploaded_by_user")
    reconciliation_runs: Mapped[list["ReconciliationRun"]] = relationship(back_populates="started_by_user")
    allocations: Mapped[list["ReconciliationAllocation"]] = relationship(back_populates="created_by_user")
    exceptions: Mapped[list["ExceptionRecord"]] = relationship(back_populates="resolved_by_user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")
