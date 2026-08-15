from src.validation.validate_sources import (
    is_valid_email,
    is_valid_phone,
    is_valid_decimal,
    is_valid_non_negative_integer,
    validate_naukri_record,
    validate_gig_record,
    validate_cbnexus_record,
)


def test_valid_email():
    assert is_valid_email(
        "person@example.com"
    )


def test_invalid_email():
    assert not is_valid_email(
        "invalid-email"
    )


def test_missing_email_is_allowed():
    assert is_valid_email("")


def test_valid_phone():
    assert is_valid_phone(
        "9000000131"
    )


def test_invalid_phone():
    assert not is_valid_phone(
        "12345"
    )


def test_missing_phone_is_allowed():
    assert is_valid_phone("")


def test_valid_decimal():
    assert is_valid_decimal("4.2")
    assert is_valid_decimal("417964")


def test_invalid_decimal():
    assert not is_valid_decimal(
        "not-a-number"
    )


def test_non_negative_integer():
    assert is_valid_non_negative_integer(0)
    assert is_valid_non_negative_integer(12)


def test_negative_integer_invalid():
    assert not is_valid_non_negative_integer(-1)


def test_valid_naukri_record():
    record = {
        "full_name": "Tanvi Gupta",
        "email": "tanvi@example.com",
        "phone": "9000000001",
        "experience_years": 2.4,
        "current_ctc": 420000,
        "applied_date": "2026-07-03",
    }

    assert validate_naukri_record(record) == []


def test_invalid_naukri_record():
    record = {
        "full_name": "",
        "email": "invalid",
        "phone": "123",
        "experience_years": "abc",
        "current_ctc": None,
        "applied_date": None,
    }

    errors = validate_naukri_record(record)

    assert "MISSING_NAME" in errors
    assert "INVALID_EMAIL" in errors
    assert "INVALID_PHONE" in errors
    assert "INVALID_EXPERIENCE" in errors
    assert "INVALID_CTC" in errors
    assert "INVALID_APPLIED_DATE" in errors


def test_valid_gig_record():
    record = {
        "worker_name": "Deepak Nair",
        "email": "deepak@example.com",
        "rate_amount": 465,
        "rate_unit": "HOUR",
        "status": "active",
    }

    assert validate_gig_record(record) == []


def test_invalid_gig_record():
    record = {
        "worker_name": "",
        "email": "invalid",
        "rate_amount": None,
        "rate_unit": "YEAR",
        "status": "unknown",
    }

    errors = validate_gig_record(record)

    assert "MISSING_NAME" in errors
    assert "INVALID_EMAIL" in errors
    assert "INVALID_RATE" in errors
    assert "INVALID_RATE_UNIT" in errors
    assert "INVALID_STATUS" in errors


def test_valid_cbnexus_record():
    record = {
        "name": "Arjun Mehta",
        "phone": "9000000131",
        "verified": True,
        "projects_completed": 9,
    }

    assert validate_cbnexus_record(record) == []


def test_invalid_cbnexus_record():
    record = {
        "name": "",
        "phone": "123",
        "verified": None,
        "projects_completed": -2,
    }

    errors = validate_cbnexus_record(record)

    assert "MISSING_NAME" in errors
    assert "INVALID_PHONE" in errors
    assert "INVALID_VERIFIED" in errors
    assert "INVALID_PROJECTS_COMPLETED" in errors