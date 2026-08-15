from decimal import Decimal


VALID_GIG_STATUSES = {
    "active",
    "inactive",
    "paused",
}


def is_valid_email(email):
    if not email:
        return True

    return (
        "@" in email
        and "." in email.rsplit("@", 1)[-1]
    )


def is_valid_phone(phone):
    if not phone:
        return True

    return (
        len(phone) == 10
        and phone.isdigit()
    )


def is_valid_decimal(value):
    if value is None:
        return False

    try:
        Decimal(str(value))
        return True
    except Exception:
        return False


def is_valid_non_negative_integer(value):
    if value is None:
        return False

    try:
        integer_value = int(value)
    except (TypeError, ValueError):
        return False

    return integer_value >= 0


def validate_naukri_record(record):
    errors = []

    if not record.get("full_name"):
        errors.append("MISSING_NAME")

    if not is_valid_email(
        record.get("email")
    ):
        errors.append("INVALID_EMAIL")

    if not is_valid_phone(
        record.get("phone")
    ):
        errors.append("INVALID_PHONE")

    if not is_valid_decimal(
        record.get("experience_years")
    ):
        errors.append("INVALID_EXPERIENCE")

    if not is_valid_decimal(
        record.get("current_ctc")
    ):
        errors.append("INVALID_CTC")

    if record.get("applied_date") is None:
        errors.append("INVALID_APPLIED_DATE")

    return errors


def validate_gig_record(record):
    errors = []

    if not record.get("worker_name"):
        errors.append("MISSING_NAME")

    if not is_valid_email(
        record.get("email")
    ):
        errors.append("INVALID_EMAIL")

    if not is_valid_decimal(
        record.get("rate_amount")
    ):
        errors.append("INVALID_RATE")

    if record.get("rate_unit") not in {
        "HOUR",
        "MONTH",
    }:
        errors.append("INVALID_RATE_UNIT")

    if record.get("status") not in VALID_GIG_STATUSES:
        errors.append("INVALID_STATUS")

    return errors


def validate_cbnexus_record(record):
    errors = []

    if not record.get("name"):
        errors.append("MISSING_NAME")

    if not is_valid_phone(
        record.get("phone")
    ):
        errors.append("INVALID_PHONE")

    if record.get("verified") is None:
        errors.append("INVALID_VERIFIED")

    if not is_valid_non_negative_integer(
        record.get("projects_completed")
    ):
        errors.append("INVALID_PROJECTS_COMPLETED")

    return errors