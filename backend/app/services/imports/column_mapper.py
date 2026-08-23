import re
from dataclasses import dataclass

HIGH_CONFIDENCE = 90
REASONABLE_CONFIDENCE = 75
UNCERTAIN_CONFIDENCE = 50

SCHEMAS = {
    "PAYMENT": {"payment_date": ("date", "txn date", "transaction date", "tx date"), "transaction_reference": ("ref", "reference", "transaction reference", "txn ref"), "payer_name": ("payer", "client", "customer", "payer name"), "amount": ("amount", "paid", "payment amount", "value"), "currency": ("currency", "ccy"), "bank_account": ("account", "bank account"), "description": ("description", "remarks", "memo")},
    "INVOICE": {"invoice_number": ("invoice", "invoice number", "invoice no", "inv"), "customer_name": ("customer", "client", "customer name"), "invoice_date": ("invoice date", "date"), "due_date": ("due", "due date"), "total_amount": ("total", "total amount", "amount", "value"), "currency": ("currency", "ccy")},
}


@dataclass(frozen=True)
class MappingSuggestion:
    source_column: str; target_field: str | None; confidence: float; method: str; status: str; reason: str | None


def normalize_header(header: str) -> str:
    value = re.sub(r"[^a-z0-9]+", " ", header.lower()).strip()
    return re.sub(r"\b(txn|trx)\b", "transaction", value)


def map_columns(columns: list[str], profile: dict[str, dict[str, object]], schema: str) -> list[MappingSuggestion]:
    targets = SCHEMAS.get(schema, {})
    used: set[str] = set(); suggestions = []
    for source in columns:
        normalized = normalize_header(source); matches = []
        for target, aliases in targets.items():
            if normalized in aliases: matches.append((target, 95))
            elif any(alias in normalized for alias in aliases): matches.append((target, 80))
        if not matches and profile.get(source, {}).get("date_percentage", 0) >= 80:
            matches = [(field, 70) for field in targets if field.endswith("date")]
        if not matches and profile.get(source, {}).get("numeric_percentage", 0) >= 80:
            matches = [(field, 65) for field in targets if field in {"amount", "total_amount"}]
        if len(matches) != 1 or matches[0][0] in used:
            suggestions.append(MappingSuggestion(source, None, 0 if not matches else matches[0][1], "COMBINED", "REVIEW" if matches else "REJECTED", "Ambiguous or unsupported column")); continue
        target, confidence = matches[0]; used.add(target)
        method = "HEADER" if confidence >= 80 else "PATTERN"
        suggestions.append(MappingSuggestion(source, target, confidence, method, "ACCEPTED" if confidence >= REASONABLE_CONFIDENCE else "REVIEW", None))
    return suggestions
