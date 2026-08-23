from app.services.imports.column_mapper import SCHEMAS


def detect_type(mappings: list[object]) -> str:
    mapped = {getattr(item, "target_field", None) for item in mappings if getattr(item, "status", None) == "ACCEPTED"}
    payment = len(mapped & {"payment_date", "transaction_reference", "payer_name", "amount"})
    invoice = len(mapped & {"invoice_number", "customer_name", "invoice_date", "due_date", "total_amount"})
    if payment >= 2 and payment > invoice: return "PAYMENT"
    if invoice >= 2 and invoice > payment: return "INVOICE"
    return "AMBIGUOUS" if payment and invoice else "UNKNOWN"


def detect_type_from_columns(columns: list[str], profile: dict[str, dict[str, object]]) -> str:
    from app.services.imports.column_mapper import map_columns
    payment = map_columns(columns, profile, "PAYMENT"); invoice = map_columns(columns, profile, "INVOICE")
    p = sum(item.status == "ACCEPTED" for item in payment); i = sum(item.status == "ACCEPTED" for item in invoice)
    if p >= 2 and p > i: return "PAYMENT"
    if i >= 2 and i > p: return "INVOICE"
    return "AMBIGUOUS" if p and i else "UNKNOWN"
