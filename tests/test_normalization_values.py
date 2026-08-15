from decimal import Decimal

from src.normalization.normalize_values import (
    normalize_city,
    normalize_email,
    normalize_phone,
    normalize_status,
    parse_ctc,
    parse_gig_rate,
    parse_projects_completed,
    parse_verified,
    normalize_skills,
)


def test_phone_normalization():
    assert normalize_phone("+91-9000000131") == "9000000131"
    assert normalize_phone("919000000231") == "9000000231"
    assert normalize_phone("09000000287") == "9000000287"
    assert normalize_phone("9000000268") == "9000000268"


def test_email_normalization():
    assert (
        normalize_email(
            " ISHA.CHOPRA95@MAILTEST.EXAMPLE.ORG "
        )
        == "isha.chopra95@mailtest.example.org"
    )


def test_city_normalization():
    assert normalize_city("bangalore") == "Bengaluru"
    assert normalize_city("BENGALURU") == "Bengaluru"
    assert normalize_city("gurugram") == "Gurgaon"
    assert normalize_city("New Delhi") == "Delhi"
    assert normalize_city("delhi ncr") == "Delhi"


def test_ctc_normalization():
    assert parse_ctc("4.2") == Decimal("420000.00")
    assert parse_ctc("7.8") == Decimal("780000.00")
    assert parse_ctc("11.9") == Decimal("1190000.00")
    assert parse_ctc("417964") == Decimal("417964.00")


def test_gig_rate_normalization():
    assert parse_gig_rate("1415/hr") == (
        Decimal("1415"),
        "HOUR",
    )

    assert parse_gig_rate("15k/month") == (
        Decimal("15000"),
        "MONTH",
    )


def test_status_normalization():
    assert normalize_status("active") == "ACTIVE"
    assert normalize_status("ACTIVE") == "ACTIVE"
    assert normalize_status("paused") == "PAUSED"


def test_verified_normalization():
    assert parse_verified("Y") is True
    assert parse_verified("yes") is True
    assert parse_verified("N") is False
    assert parse_verified("no") is False


def test_projects_completed():
    assert parse_projects_completed("13") == 13
    assert parse_projects_completed("0") == 0
    assert parse_projects_completed("-1") is None


def test_skills_normalization():
    assert normalize_skills(
        "SQL, Python,  JavaScript"
    ) == [
        "sql",
        "python",
        "javascript",
    ]