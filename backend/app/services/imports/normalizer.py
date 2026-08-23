from datetime import datetime
from decimal import Decimal, InvalidOperation


def normalize_value(field: str, value: str) -> str:
    value = value.strip()
    if field in {"amount", "total_amount"}: return format(Decimal(value.replace(",", "")), ".2f")
    if field.endswith("date"):
        for pattern in ("%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%d/%m/%Y"):
            try: return datetime.strptime(value, pattern).date().isoformat()
            except ValueError: continue
        raise ValueError("invalid date")
    return value
