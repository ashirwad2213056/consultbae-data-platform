from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


CITY_MAP = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "delhi ncr": "Delhi",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "noida": "Noida",
    "pune": "Pune",
}


STATUS_MAP = {
    "active": "ACTIVE",
    "inactive": "INACTIVE",
    "paused": "PAUSED",
}


def clean_text(value: object) -> str:
    if value is None:
        return ""

    return " ".join(str(value).strip().split())


def normalize_email(value: object) -> str:
    return clean_text(value).lower()


def normalize_phone(value: object) -> str:
    value = clean_text(value)

    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10:
        return digits

    return ""


def normalize_name(value: object) -> str:
    return clean_text(value)


def normalize_city(value: object) -> str:
    city = clean_text(value).lower()

    return CITY_MAP.get(city, clean_text(value))


def parse_experience(value: object) -> Decimal | None:
    text = clean_text(value)

    if not text:
        return None

    try:
        result = Decimal(text)
    except InvalidOperation:
        return None

    if result < 0:
        return None

    return result.quantize(Decimal("0.01"))


def parse_ctc(value: object) -> Decimal | None:
    text = clean_text(value)

    if not text:
        return None

    try:
        result = Decimal(text)
    except InvalidOperation:
        return None

    if result <= 0:
        return None

    # Values below 100 represent lakh-style CTC
    # in the source dataset.
    if result < Decimal("100"):
        result = result * Decimal("100000")

    return result.quantize(Decimal("0.01"))


DATE_FORMATS = (
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%d %b %Y",
    "%d %B %Y",
)


def parse_applied_date(value: object) -> date | None:
    text = clean_text(value)

    if not text:
        return None

    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(
                text,
                date_format,
            ).date()
        except ValueError:
            continue

    return None


def parse_gig_rate(
    value: object,
) -> tuple[Decimal | None, str | None]:

    text = clean_text(value).lower()

    if not text:
        return None, None

    hourly_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*/\s*hr",
        text,
    )

    if hourly_match:
        return (
            Decimal(hourly_match.group(1)),
            "HOUR",
        )

    monthly_match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*k\s*/\s*month",
        text,
    )

    if monthly_match:
        amount = (
            Decimal(monthly_match.group(1))
            * Decimal("1000")
        )

        return amount, "MONTH"

    return None, None


def normalize_status(value: object) -> str:
    status = clean_text(value).lower()

    return STATUS_MAP.get(status, "")


def parse_verified(value: object) -> bool | None:
    verified = clean_text(value).lower()

    if verified in {"y", "yes"}:
        return True

    if verified in {"n", "no"}:
        return False

    return None


def parse_projects_completed(
    value: object,
) -> int | None:

    text = clean_text(value)

    if not text:
        return None

    try:
        result = int(text)
    except ValueError:
        return None

    if result < 0:
        return None

    return result


def normalize_skill(value: object) -> str:
    return clean_text(value).lower()


def normalize_skills(value: object) -> list[str]:
    text = clean_text(value)

    if not text:
        return []

    skills = [
        normalize_skill(skill)
        for skill in text.split(",")
    ]

    return [
        skill
        for skill in skills
        if skill
    ]