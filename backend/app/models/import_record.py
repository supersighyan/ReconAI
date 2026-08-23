import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ImportRecord(Base):
    __tablename__ = "import_records"
    __table_args__ = (
        CheckConstraint("row_number > 0", name="ck_import_records_row_number_positive"),
        Index("ix_import_records_batch_id_row_number", "batch_id", "row_number"),
        Index("ix_import_records_batch_id", "batch_id"),
        Index("ix_import_records_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_data: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    normalized_data: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    errors: Mapped[list[dict[str, str]] | None] = mapped_column(JSONB, nullable=True)
    warnings: Mapped[list[dict[str, str]] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    batch: Mapped["ImportBatch"] = relationship(back_populates="import_records")
