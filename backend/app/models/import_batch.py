import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    record_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    valid_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    detected_encoding: Mapped[str | None] = mapped_column(String(50), nullable=True)
    detected_delimiter: Mapped[str | None] = mapped_column(String(10), nullable=True)
    has_header: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    detected_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    mapping_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    validation_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    uploaded_by_user: Mapped["User | None"] = relationship(back_populates="import_batches")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="source_batch")
    payments: Mapped[list["Payment"]] = relationship(back_populates="source_batch")
    import_records: Mapped[list["ImportRecord"]] = relationship(back_populates="batch")
    column_mappings: Mapped[list["ImportColumnMapping"]] = relationship(back_populates="batch")
