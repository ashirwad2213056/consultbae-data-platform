from decimal import Decimal

from src.normalization.validation_rules import (
    is_malformed_gig_record,
    is_valid_email,
    is_valid_phone,
    is_valid_status,
    is_valid_rate,
    validate_cbnexus_record,
    validate_gig_record,
    validate_naukri_record,
)


def test_valid_email():
    assert is_valid_email(
        "worker@example.com"
    )


def test_invalid_email():
    assert not is_valid_email(
        "not-an-email"
    )


def test_valid_phone():
    assert is_valid_phone(
        "9000000131"
    )


def test_invalid_phone():
    assert not is_valid_phone(
        "919000000231"
    )


def test_valid_status():
    assert is_valid_status("ACTIVE")


def test_invalid_status():
    assert not is_valid_status("PUNE")


def test_valid_rate():
    assert is_valid_rate(
        Decimal("1415"),
        "HOUR",
    )

    assert is_valid_rate(
        Decimal("15000"),
        "MONTH",
    )


def test_malformed_gig_record():
    record = {
        "email": "react, javascript, mysql",
        "worker_name":
            "ISHA.CHOPRA95@MAILTEST.EXAMPLE.ORG",
        "rate": "Isha Chopra",
        "location": "1406/hr",
        "status": "Pune",
        "skills": "active",
    }

    assert is_malformed_gig_record(record)


def test_valid_gig_record():
    record = {
        "email": "varun.jain29@example.com",
        "worker_name": "Varun Jain",
        "rate": "1415/hr",
        "location": "Pune",
        "status": "Active",
        "skills":
            "n8n, web scraping, fastapi",
    }

    assert not is_malformed_gig_record(record)


def test_naukri_validation():
    record = {
        "email": "worker@example.com",
        "phone_10": "9000000131",
        "experience_years": Decimal("4.2"),
        "current_ctc": Decimal("420000"),
        "applied_date": "2026-07-24",
    }

    assert validate_naukri_record(record) == []


def test_gig_validation():
    record = {
        "email": "worker@example.com",
        "rate_amount": Decimal("1415"),
        "rate_unit": "HOUR",
        "status": "ACTIVE",
    }

    assert validate_gig_record(record) == []


def test_cbnexus_validation():
    record = {
        "phone_10": "9000000131",
        "verified": True,
        "projects_completed": 13,
    }

    assert validate_cbnexus_record(record) == []