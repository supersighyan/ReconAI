import re
from collections import Counter


def profile_rows(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    columns = {key for row in rows for key in row if not key.startswith("_")}
    profile: dict[str, dict[str, object]] = {}
    for column in columns:
        values = [str(row.get(column, "")).strip() for row in rows]
        nonempty = [value for value in values if value]
        total = len(values) or 1
        profile[column] = {
            "empty_percentage": round(100 * (len(values) - len(nonempty)) / total, 2),
            "numeric_percentage": _percentage(nonempty, _numeric),
            "date_percentage": _percentage(nonempty, _date_like),
            "currency_percentage": _percentage(nonempty, lambda value: bool(re.fullmatch(r"[A-Z]{3}", value))),
            "reference_percentage": _percentage(nonempty, lambda value: bool(re.fullmatch(r"[A-Za-z]{1,6}[- ]?\d{2,}", value))),
            "max_length": max(map(len, values), default=0), "min_length": min(map(len, nonempty), default=0),
            "common_values": [value for value, _ in Counter(nonempty).most_common(5)], "example_values": nonempty[:3],
        }
    return profile


def _percentage(values: list[str], predicate: object) -> float:
    return round(100 * sum(bool(predicate(value)) for value in values) / len(values), 2) if values else 0.0


def _numeric(value: str) -> bool:
    try: float(value.replace(",", "")); return True
    except ValueError: return False


def _date_like(value: str) -> bool:
    return bool(re.fullmatch(r"\d{1,4}[/-]\d{1,2}[/-]\d{1,4}", value))
