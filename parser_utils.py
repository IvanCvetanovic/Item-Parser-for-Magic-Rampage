import re


def parse_scalar(value):
    """Parse booleans and simple numeric literals from ENML-like assignments."""
    if not isinstance(value, str):
        return value

    text = value.strip().rstrip(";")
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    if re.fullmatch(r"[+-]?(?:\d+\.\d*|\.\d+)", text):
        return float(text)

    return text


def process_boost(value):
    """Convert a multiplier into a whole-number percentage bonus."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0
    return 0 if numeric in (0.0, 1.0) else round((numeric - 1) * 100)


def sanitize_resource_name(name, fallback):
    """Normalize an item name for generated Android resource identifiers."""
    text = str(name or fallback).strip().lower()
    text = text.replace(" ", "_").replace("'", "")
    text = text.replace("+", "_plus").replace("-", "")
    return text
