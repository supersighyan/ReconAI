from decimal import Decimal, InvalidOperation

from app.services.imports.normalizer import normalize_value

REQUIRED = {"PAYMENT": {"payment_date", "payer_name", "amount"}, "INVOICE": {"invoice_number", "customer_name", "invoice_date", "total_amount"}}


def validate_row(raw_data: dict[str, str], mappings: list[object], record_type: str, parser_errors: list[dict[str, str]] | None = None) -> dict[str, object]:
    errors = list(parser_errors or []); warnings = []; normalized: dict[str, str] = {}
    accepted = [item for item in mappings if getattr(item, "status", None) == "ACCEPTED" and getattr(item, "target_field", None)]
    for item in accepted:
        field, value = item.target_field, raw_data.get(item.source_column, "")
        if not value.strip(): continue
        try: normalized[field] = normalize_value(field, value)
        except (ValueError, InvalidOperation): errors.append({"field": field, "message": "Invalid value"})
    for field in REQUIRED.get(record_type, set()):
        if not normalized.get(field): errors.append({"field": field, "message": "Required field is missing"})
    amount = normalized.get("amount") or normalized.get("total_amount")
    if amount:
        try:
            if Decimal(amount) < 0: errors.append({"field": "amount", "message": "Negative amount is not allowed"})
        except InvalidOperation: errors.append({"field": "amount", "message": "Invalid amount"})
    currency = normalized.get("currency")
    if currency and (len(currency) != 3 or not currency.isalpha()): warnings.append({"field": "currency", "message": "Unrecognized currency code"})
    status = "INVALID" if errors else "WARNING" if warnings else "VALID"
    return {"status": status, "errors": errors or None, "warnings": warnings or None, "normalized_data": normalized or None}
