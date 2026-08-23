import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ImportColumnMapping(Base):
    __tablename__ = "import_column_mappings"
    __table_args__ = (
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="ck_import_column_mappings_confidence_range"),
        Index("ix_import_column_mappings_batch_id", "batch_id"),
        Index("ix_import_column_mappings_batch_id_source_column", "batch_id", "source_column"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("import_batches.id"), nullable=False)
    source_column: Mapped[str] = mapped_column(String(255), nullable=False)
    target_field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    batch: Mapped["ImportBatch"] = relationship(back_populates="column_mappings")
