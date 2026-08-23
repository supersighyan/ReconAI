from io import BytesIO
import uuid

from fastapi.testclient import TestClient
import pytest

from app.services.imports.column_mapper import map_columns, normalize_header
from app.services.imports.csv_inspector import inspect_csv
from app.services.imports.csv_parser import parse_csv
from app.services.imports.data_profiler import profile_rows
from app.services.imports.file_hash import sha256_file
from app.services.imports.type_detector import detect_type_from_columns
from app.services.imports.validator import validate_row


class _PreviewSession:
    def __init__(self) -> None:
        self.added: list[object] = []

    def begin(self) -> "_PreviewSession": return self
    def __enter__(self) -> "_PreviewSession": return self
    def __exit__(self, *_: object) -> None: return None
    def add(self, item: object) -> None: self.added.append(item)
    def flush(self) -> None:
        for item in self.added:
            if getattr(item, "id", None) is None: item.id = uuid.uuid4()
    def rollback(self) -> None: pass


def test_csv_inspection_parsing_and_hashing() -> None:
    content = b"Date;Ref;Client;Value\n08/21/2026;TX-1023;ABC Corp;50,000.00\n"
    inspection = inspect_csv(content)
    rows = parse_csv(content, inspection)
    assert (inspection.encoding, inspection.delimiter, inspection.has_header) == ("utf-8-sig", ";", True)
    assert rows[0].raw_data["Client"] == "ABC Corp"
    assert sha256_file(BytesIO(b"abc")) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


@pytest.mark.parametrize("delimiter", [",", "\t", "|"])
def test_supported_delimiters_and_inspection_edge_cases(delimiter: str) -> None:
    inspection = inspect_csv(f"Date{delimiter}Amount{delimiter}Empty\n2026-08-21{delimiter}10{delimiter}\n".encode())
    assert inspection.delimiter == delimiter
    assert inspection.empty_columns == ["Empty"]
    assert inspection.has_header


def test_encoding_duplicate_headers_and_malformed_rows() -> None:
    fallback = inspect_csv(b"Name,Amount\nJos\xe9,10\n")
    malformed = inspect_csv(b"Date,Date,Amount\n2026-01-01,2026-01-02,10,extra\n")
    assert fallback.encoding == "cp1252"
    assert malformed.duplicate_columns == ["Date"]
    assert malformed.malformed_rows == [2]


def test_mapping_detection_and_validation_preserve_raw_data() -> None:
    rows = [{"Date": "08/21/26", "Ref": "TX-1001", "Client": "  ABC Corp ", "Amount": "50000"}]
    profile = profile_rows(rows)
    mappings = map_columns(list(rows[0]), profile, "PAYMENT")
    result = validate_row(rows[0], mappings, "PAYMENT")
    assert normalize_header("Txn_Date") == "transaction date"
    assert detect_type_from_columns(list(rows[0]), profile) == "PAYMENT"
    assert result["status"] == "VALID"
    assert result["normalized_data"]["amount"] == "50000.00"
    assert rows[0]["Client"] == "  ABC Corp "


def test_invalid_negative_amount_is_rejected() -> None:
    rows = [{"Date": "2026-08-21", "Client": "ABC", "Amount": "-1"}]
    mappings = map_columns(list(rows[0]), profile_rows(rows), "PAYMENT")
    result = validate_row(rows[0], mappings, "PAYMENT")
    assert result["status"] == "INVALID"


def test_preview_endpoint_stages_only_import_data() -> None:
    from app.core.database import get_db
    from app.main import create_app
    from app.models.invoice import Invoice
    from app.models.payment import Payment

    session = _PreviewSession()
    app = create_app()
    app.dependency_overrides[get_db] = lambda: session
    response = TestClient(app).post("/imports/preview", files={"file": ("payments.csv", b"Date,Ref,Client,Amount\n08/21/2026,TX-1,ABC,10\n", "text/csv")})
    assert response.status_code == 200
    assert response.json()["summary"]["total_rows"] == 1
    assert not any(isinstance(item, (Payment, Invoice)) for item in session.added)
