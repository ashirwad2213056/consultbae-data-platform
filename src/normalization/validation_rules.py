from __future__ import annotations

import re
from decimal import Decimal


VALID_STATUSES = {
    "ACTIVE",
    "INACTIVE",
    "PAUSED",
}


def is_valid_email(email: str) -> bool:
    if not email:
        return False

    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email,
        )
    )


def is_valid_phone(phone: str) -> bool:
    return bool(
        re.fullmatch(
            r"\d{10}",
            phone,
        )
    )


def is_valid_experience(
    experience: Decimal | None,
) -> bool:
    if experience is None:
        return False

    return experience >= Decimal("0")


def is_valid_ctc(
    ctc: Decimal | None,
) -> bool:
    if ctc is None:
        return False

    return ctc > Decimal("0")


def is_valid_status(status: str) -> bool:
    return status in VALID_STATUSES


def is_valid_rate(
    amount: Decimal | None,
    unit: str | None,
) -> bool:
    if amount is None or unit is None:
        return False

    if amount <= Decimal("0"):
        return False

    return unit in {"HOUR", "MONTH"}


def is_valid_verified(
    verified: bool | None,
) -> bool:
    return verified is not None


def is_valid_projects_completed(
    projects: int | None,
) -> bool:
    return projects is not None and projects >= 0



def validate_naukri_record(record: dict) -> list[str]:
    errors = []

    if not is_valid_email(record.get("email", "")):
        errors.append("INVALID_EMAIL")

    if not is_valid_phone(record.get("phone_10", "")):
        errors.append("INVALID_PHONE")

    if not is_valid_experience(
        record.get("experience_years")
    ):
        errors.append("INVALID_EXPERIENCE")

    if not is_valid_ctc(
        record.get("current_ctc")
    ):
        errors.append("INVALID_CTC")

    if record.get("applied_date") is None:
        errors.append("INVALID_DATE")

    return errors


def validate_gig_record(record: dict) -> list[str]:
    errors = []

    if not is_valid_email(record.get("email", "")):
        errors.append("INVALID_EMAIL")

    if not is_valid_rate(
        record.get("rate_amount"),
        record.get("rate_unit"),
    ):
        errors.append("INVALID_RATE")

    if not is_valid_status(
        record.get("status", "")
    ):
        errors.append("INVALID_STATUS")

    return errors


def validate_cbnexus_record(record: dict) -> list[str]:
    errors = []

    if not is_valid_phone(
        record.get("phone_10", "")
    ):
        errors.append("INVALID_PHONE")

    if not is_valid_verified(
        record.get("verified")
    ):
        errors.append("INVALID_VERIFIED")

    if not is_valid_projects_completed(
        record.get("projects_completed")
    ):
        errors.append(
            "INVALID_PROJECTS_COMPLETED"
        )

    return errors


def is_malformed_gig_record(record: dict) -> bool:
    """
    Detect field-shifted Gig records where values appear
    in the wrong columns.
    """

    email = record.get("email", "")
    worker_name = record.get("worker_name", "")
    rate = record.get("rate", "")
    location = record.get("location", "")
    status = record.get("status", "")
    skills = record.get("skills", "")

    # A valid Gig email must look like an email.
    if email and not is_valid_email(email):
        return True

    # Worker name should not look like an email.
    if "@" in worker_name:
        return True

    # Rate must contain /hr or /month.
    if rate and not re.fullmatch(
        r"\d+(?:\.\d+)?\s*(?:/hr|k/month)",
        rate.lower().strip(),
    ):
        return True

    # Status should be one of the known source statuses.
    if status and status.lower().strip() not in {
        "active",
        "inactive",
        "paused",
    }:
        return True

    return False