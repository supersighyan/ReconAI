"""Add CSV import staging and metadata.

Revision ID: 20260824_0002
Revises: 20260824_0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260824_0002"
down_revision = "20260824_0001"
branch_labels = depends_on = None


def upgrade() -> None:
    op.add_column("import_batches", sa.Column("file_size", sa.BigInteger()))
    op.add_column("import_batches", sa.Column("detected_encoding", sa.String(50)))
    op.add_column("import_batches", sa.Column("detected_delimiter", sa.String(10)))
    op.add_column("import_batches", sa.Column("has_header", sa.Boolean()))
    op.add_column("import_batches", sa.Column("detected_type", sa.String(30)))
    op.add_column("import_batches", sa.Column("mapping_status", sa.String(30)))
    op.add_column("import_batches", sa.Column("validation_status", sa.String(30)))
    op.create_table("import_records", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_batches.id"), nullable=False), sa.Column("row_number", sa.Integer(), nullable=False), sa.Column("raw_data", postgresql.JSONB(), nullable=False), sa.Column("normalized_data", postgresql.JSONB()), sa.Column("status", sa.String(30), nullable=False), sa.Column("errors", postgresql.JSONB()), sa.Column("warnings", postgresql.JSONB()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.CheckConstraint("row_number > 0", name="ck_import_records_row_number_positive"))
    op.create_index("ix_import_records_batch_id_row_number", "import_records", ["batch_id", "row_number"]); op.create_index("ix_import_records_batch_id", "import_records", ["batch_id"]); op.create_index("ix_import_records_status", "import_records", ["status"])
    op.create_table("import_column_mappings", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("import_batches.id"), nullable=False), sa.Column("source_column", sa.String(255), nullable=False), sa.Column("target_field", sa.String(100)), sa.Column("confidence", sa.Numeric(5, 2)), sa.Column("method", sa.String(30), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.CheckConstraint("confidence >= 0 AND confidence <= 100", name="ck_import_column_mappings_confidence_range"))
    op.create_index("ix_import_column_mappings_batch_id", "import_column_mappings", ["batch_id"]); op.create_index("ix_import_column_mappings_batch_id_source_column", "import_column_mappings", ["batch_id", "source_column"])


def downgrade() -> None:
    op.drop_table("import_column_mappings"); op.drop_table("import_records")
    for name in ("validation_status", "mapping_status", "detected_type", "has_header", "detected_delimiter", "detected_encoding", "file_size"): op.drop_column("import_batches", name)
