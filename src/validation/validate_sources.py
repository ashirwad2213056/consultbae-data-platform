from decimal import Decimal


VALID_GIG_STATUSES = {
    "active",
    "inactive",
    "paused",
}


def detect_gig_column_shift(record):
    """
    Detect the known Gig CSV column-shift pattern.

    Expected:
        email_id, worker_name, rate, location, status, skill_tags

    Shifted pattern:
        skill_tags, email_id, worker_name, rate, location, status

    The pattern is considered structurally shifted when:
        - first field looks like a skill list
        - second field looks like an email
        - third field looks like a worker name
        - fourth field looks like a rate
        - fifth field looks like a location
        - sixth field looks like a status
    """

    email_id = str(
        record.get("email_id") or ""
    ).strip()

    worker_name = str(
        record.get("worker_name") or ""
    ).strip()

    rate = str(
        record.get("rate") or ""
    ).strip().lower()

    location = str(
        record.get("location") or ""
    ).strip()

    status = str(
        record.get("status") or ""
    ).strip().lower()

    skill_tags = str(
        record.get("skill_tags") or ""
    ).strip()

    looks_like_email = (
        "@" in email_id
        and "." in email_id.rsplit("@", 1)[-1]
    )

    looks_like_rate = (
        rate.endswith("/hr")
        or rate.endswith("/month")
    )

    looks_like_status = (
        status in VALID_GIG_STATUSES
    )

    first_field_looks_like_skills = (
        "," in email_id
        and bool(email_id)
    )

    return (
        first_field_looks_like_skills
        and looks_like_email is False
        and "@" in worker_name
        and not looks_like_rate
        and not looks_like_status
        and skill_tags in VALID_GIG_STATUSES
    )


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

    if detect_gig_column_shift(record):
        errors.append("GIG_COLUMN_SHIFT")

    if not record.get("worker_name"):
        errors.append("MISSING_NAME")

    if not is_valid_email(
        record.get("email_id")
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