import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from src.normalization.validation_rules import (
    is_malformed_gig_record,
)


CITY_MAP = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "delhi ncr": "Delhi",
    "noida": "Noida",
    "pune": "Pune",
}


STATUS_MAP = {
    "active": "ACTIVE",
    "inactive": "INACTIVE",
    "paused": "PAUSED",
}


VERIFIED_MAP = {
    "y": True,
    "yes": True,
    "n": False,
    "no": False,
}

def repair_gig_column_shift(record):
    """
    Repair the known six-field left-shift pattern in Gig data.

    Original received structure:
        skill_tags, email_id, worker_name,
        rate, location, status

    Expected structure:
        email_id, worker_name, rate,
        location, status, skill_tags
    """

    if not is_malformed_gig_record(record):
        return record

    return {
        **record,
        "email_id": record["worker_name"],
        "worker_name": record["rate"],
        "rate": record["location"],
        "location": record["status"],
        "status": record["skill_tags"],
        "skill_tags": record["email_id"],
    }


def normalize_text(value):
    if value is None:
        return ""

    return " ".join(
        str(value).strip().split()
    )


def normalize_email(value):
    value = normalize_text(value)

    if not value:
        return ""

    return value.lower()


def normalize_phone(value):
    if value is None:
        return ""

    digits = "".join(
        character
        for character in str(value)
        if character.isdigit()
    )

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10:
        return digits

    return ""


def normalize_name(value):
    return normalize_text(value)


def normalize_city(value):
    value = normalize_text(value).lower()

    if not value:
        return ""

    return CITY_MAP.get(
        value,
        value.title(),
    )


def normalize_status(value):
    value = normalize_text(value).lower()

    if not value:
        return ""

    return STATUS_MAP.get(
        value,
        "",
    )


def normalize_verified(value):
    value = normalize_text(value).lower()

    if not value:
        return None

    return VERIFIED_MAP.get(
        value,
    )


def parse_decimal(value):
    value = normalize_text(value)

    if not value:
        return None

    try:
        return Decimal(value)
    except InvalidOperation:
        return None

def parse_gig_rate(value):
    value = normalize_text(value).lower()

    if not value:
        return None, None

    match = re.fullmatch(
        r"([0-9]+(?:\.[0-9]+)?)\s*(k)?\s*(/hr|/month)",
        value,
    )

    if not match:
        return None, None

    amount = Decimal(match.group(1))

    if match.group(2) == "k":
        amount *= Decimal("1000")

    unit = match.group(3)

    if unit == "/hr":
        return amount, "HOUR"

    if unit == "/month":
        return amount, "MONTH"

    return None, None

def parse_ctc(value):
    """
    Normalize Naukri Current CTC to annual INR.

    Source-specific rule:
    - Values below 100 represent CTC in lakhs.
    - Values >= 100 represent absolute INR.
    """

    amount = parse_decimal(value)

    if amount is None:
        return None

    if amount < Decimal("100"):
        return amount * Decimal("100000")

    return amount


def parse_applied_date(value):
    """
    Normalize Naukri Applied Date into a Python date.

    Supported source formats:
    - YYYY-MM-DD
    - DD-MM-YYYY
    - MM/DD/YYYY
    - DD Mon YYYY
    - D Mon YYYY
    """

    value = normalize_text(value)

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(
                value,
                date_format,
            ).date()
        except ValueError:
            continue

    return None