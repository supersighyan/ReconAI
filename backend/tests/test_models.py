from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import UUID

import app.models  # noqa: F401
from app.core.database import Base
from app.models.reconciliation_allocation import ReconciliationAllocation
from app.models.reconciliation_candidate import ReconciliationCandidate


EXPECTED_TABLES = {
    "users", "import_batches", "invoices", "payments", "reconciliation_runs",
    "reconciliation_candidates", "reconciliation_allocations", "exceptions", "audit_logs",
}


def test_all_domain_tables_are_registered() -> None:
    assert EXPECTED_TABLES <= set(Base.metadata.tables)


def test_primary_keys_use_postgresql_uuid() -> None:
    for table_name in EXPECTED_TABLES:
        primary_key = list(Base.metadata.tables[table_name].primary_key.columns)
        assert len(primary_key) == 1
        assert isinstance(primary_key[0].type, UUID)


def test_financial_columns_use_numeric() -> None:
    for table_name, column_name in (("invoices", "total_amount"), ("payments", "amount"), ("reconciliation_allocations", "allocated_amount")):
        column = Base.metadata.tables[table_name].c[column_name]
        assert isinstance(column.type, Numeric)
        assert (column.type.precision, column.type.scale) == (18, 2)


def test_candidates_and_allocations_are_distinct_financial_concepts() -> None:
    assert ReconciliationCandidate.__table__.name != ReconciliationAllocation.__table__.name
    assert "allocated_amount" not in ReconciliationCandidate.__table__.c


def test_foreign_keys_and_relationships_are_configured() -> None:
    candidate_foreign_keys = {foreign_key.target_fullname for foreign_key in Base.metadata.tables["reconciliation_candidates"].foreign_keys}
    assert candidate_foreign_keys == {"reconciliation_runs.id", "payments.id", "invoices.id"}
    assert {relationship.key for relationship in ReconciliationAllocation.__mapper__.relationships} == {"run", "payment", "invoice", "created_by_user"}


def test_important_constraints_and_indexes_exist() -> None:
    allocation_constraints = {constraint.name for constraint in Base.metadata.tables["reconciliation_allocations"].constraints}
    assert "ck_allocations_amount_positive" in allocation_constraints
    candidate_constraints = {constraint.name for constraint in Base.metadata.tables["reconciliation_candidates"].constraints}
    assert "ck_candidates_score_range" in candidate_constraints
    assert {index.name for index in Base.metadata.tables["invoices"].indexes} >= {"ix_invoices_invoice_number", "ix_invoices_normalized_customer", "ix_invoices_status", "ix_invoices_due_date"}
    assert {index.name for index in Base.metadata.tables["audit_logs"].indexes} >= {"ix_audit_logs_entity_type_entity_id", "ix_audit_logs_created_at"}
