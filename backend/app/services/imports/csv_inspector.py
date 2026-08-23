import csv
from dataclasses import dataclass

DELIMITERS = (",", ";", "\t", "|")


@dataclass(frozen=True)
class CsvInspection:
    encoding: str
    delimiter: str
    has_header: bool
    columns: list[str]
    row_count: int
    column_count: int
    malformed_rows: list[int]
    empty_columns: list[str]
    duplicate_columns: list[str]


def _decode(content: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV content could not be decoded safely")


def inspect_csv(content: bytes) -> CsvInspection:
    text, encoding = _decode(content)
    sample = text[:8192]
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters="".join(DELIMITERS)).delimiter
    except csv.Error:
        delimiter = max(DELIMITERS, key=lambda candidate: sample.count(candidate))
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if not rows:
        return CsvInspection(encoding, delimiter, False, [], 0, 0, [], [], [])
    first = rows[0]
    has_header = bool(first) and any(not _looks_number_or_date(value) for value in first) and len(rows) > 1
    columns = first if has_header else [f"column_{index + 1}" for index in range(max(map(len, rows)))]
    data_rows = rows[1:] if has_header else rows
    expected = len(columns)
    malformed = [index + (2 if has_header else 1) for index, row in enumerate(data_rows) if len(row) != expected]
    empty = [column for index, column in enumerate(columns) if not any(index < len(row) and row[index].strip() for row in data_rows)]
    duplicates = sorted({column for column in columns if columns.count(column) > 1})
    return CsvInspection(encoding, delimiter, has_header, columns, len(data_rows), expected, malformed, empty, duplicates)


def _looks_number_or_date(value: str) -> bool:
    value = value.strip()
    return bool(value) and (value.replace(",", "").replace(".", "", 1).isdigit() or "/" in value or "-" in value)
