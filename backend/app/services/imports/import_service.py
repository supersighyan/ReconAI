from io import BytesIO

from sqlalchemy.orm import Session

from app.models.import_batch import ImportBatch
from app.models.import_column_mapping import ImportColumnMapping
from app.models.import_record import ImportRecord
from app.services.imports.column_mapper import map_columns
from app.services.imports.csv_inspector import inspect_csv
from app.services.imports.csv_parser import parse_csv
from app.services.imports.data_profiler import profile_rows
from app.services.imports.file_hash import sha256_file
from app.services.imports.type_detector import detect_type_from_columns
from app.services.imports.validator import validate_row


def preview_import(session: Session, content: bytes, filename: str) -> dict[str, object]:
    inspection = inspect_csv(content)
    rows = parse_csv(content, inspection)
    profile = profile_rows([row.raw_data for row in rows])
    detected_type = detect_type_from_columns(inspection.columns, profile)
    schema = detected_type if detected_type in {"PAYMENT", "INVOICE"} else "PAYMENT"
    mappings = map_columns(inspection.columns, profile, schema)
    mapping_status = "READY" if mappings and all(item.status == "ACCEPTED" for item in mappings if item.target_field) else "NEEDS_REVIEW"
    batch = ImportBatch(filename=filename[:255], source_type="CSV", file_hash=sha256_file(BytesIO(content)), file_size=len(content), detected_encoding=inspection.encoding, detected_delimiter=inspection.delimiter, has_header=inspection.has_header, detected_type=detected_type, mapping_status=mapping_status, validation_status="PENDING", status="PREVIEW", record_count=inspection.row_count)
    try:
        with session.begin():
            session.add(batch); session.flush()
            for mapping in mappings:
                session.add(ImportColumnMapping(batch_id=batch.id, source_column=mapping.source_column, target_field=mapping.target_field, confidence=mapping.confidence, method=mapping.method, status=mapping.status, reason=mapping.reason))
            results = [validate_row(row.raw_data, mappings, detected_type, row.errors) for row in rows]
            for row, result in zip(rows, results, strict=True):
                session.add(ImportRecord(batch_id=batch.id, row_number=row.row_number, raw_data=row.raw_data, normalized_data=result["normalized_data"], status=result["status"], errors=result["errors"], warnings=result["warnings"]))
            counts = {name: sum(result["status"] == name for result in results) for name in ("VALID", "WARNING", "NEEDS_REVIEW", "INVALID")}
            batch.valid_count = counts["VALID"]; batch.error_count = counts["INVALID"]
            batch.validation_status = "ERROR" if counts["INVALID"] else "WARNING" if counts["WARNING"] or mapping_status == "NEEDS_REVIEW" else "VALID"
        return {"batch_id": str(batch.id), "detected_type": detected_type, "encoding": inspection.encoding, "delimiter": inspection.delimiter, "has_header": inspection.has_header, "row_count": inspection.row_count, "column_count": inspection.column_count, "mapping_status": mapping_status, "validation_status": batch.validation_status, "column_mappings": [{"source_column": item.source_column, "target_field": item.target_field, "confidence": item.confidence, "method": item.method, "status": item.status} for item in mappings], "summary": {"total_rows": len(rows), "valid_rows": counts["VALID"], "warning_rows": counts["WARNING"], "review_rows": counts["NEEDS_REVIEW"], "invalid_rows": counts["INVALID"]}}
    except Exception:
        session.rollback(); raise
