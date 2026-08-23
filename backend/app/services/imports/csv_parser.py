import csv
from dataclasses import dataclass

from app.services.imports.csv_inspector import CsvInspection, _decode


@dataclass(frozen=True)
class ParsedRow:
    row_number: int
    raw_data: dict[str, str]
    errors: list[dict[str, str]]


def parse_csv(content: bytes, inspection: CsvInspection) -> list[ParsedRow]:
    text, _ = _decode(content)
    rows = csv.reader(text.splitlines(), delimiter=inspection.delimiter)
    next(rows, None) if inspection.has_header else None
    columns = _unique_columns(inspection.columns)
    offset = 2 if inspection.has_header else 1
    parsed: list[ParsedRow] = []
    for index, values in enumerate(rows, offset):
        errors = []
        if len(values) != len(columns):
            errors.append({"code": "malformed_row", "message": "Column count does not match header"})
        raw = {column: values[position] if position < len(values) else "" for position, column in enumerate(columns)}
        if len(values) > len(columns):
            raw["_extra_values"] = values[len(columns):]
        parsed.append(ParsedRow(index, raw, errors))
    return parsed


def _unique_columns(columns: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    for column in columns:
        seen[column] = seen.get(column, 0) + 1
        result.append(column if seen[column] == 1 else f"{column}__{seen[column]}")
    return result
