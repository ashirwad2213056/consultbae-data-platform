from decimal import Decimal
from datetime import date
from src.normalization.normalize_sources import (
    normalize_email,
    normalize_phone,
    normalize_city,
    normalize_status,
    normalize_verified,
    parse_gig_rate,
    parse_ctc,
    parse_applied_date,
)


def test_normalize_email():
    assert (
        normalize_email(
            " Tanvi.Gupta31@EXAMPLE.COM "
        )
        == "tanvi.gupta31@example.com"
    )


def test_normalize_phone():
    assert (
        normalize_phone("+91-9000000131")
        == "9000000131"
    )

    assert (
        normalize_phone("919000000231")
        == "9000000231"
    )

    assert (
        normalize_phone("09000000287")
        == "9000000287"
    )


def test_phone_is_not_prefixed_with_country_code():
    result = normalize_phone(
        "9000000254"
    )

    assert result == "9000000254"
    assert not result.startswith("91")


def test_normalize_city():
    assert normalize_city("BANGALORE") == "Bengaluru"
    assert normalize_city("bengaluru") == "Bengaluru"
    assert normalize_city("GURUGRAM") == "Gurgaon"
    assert normalize_city("PUNE") == "Pune"


def test_normalize_status():
    assert normalize_status("ACTIVE") == "active"
    assert normalize_status("Inactive") == "inactive"
    assert normalize_status("paused") == "paused"


def test_normalize_verified():
    assert normalize_verified("Y") is True
    assert normalize_verified("yes") is True
    assert normalize_verified("N") is False
    assert normalize_verified("No") is False


def test_parse_gig_rate_hour():
    amount, unit = parse_gig_rate("1415/hr")

    assert amount == Decimal("1415")
    assert unit == "HOUR"


def test_parse_gig_rate_month():
    amount, unit = parse_gig_rate("15k/month")

    assert amount == Decimal("15000")
    assert unit == "MONTH"

def test_parse_gig_rate_decimal_month():
    amount, unit = parse_gig_rate("73k/month")

    assert amount == Decimal("73000")
    assert unit == "MONTH"

def test_parse_ctc_lakh_value():
    assert (
        parse_ctc("4.2")
        == Decimal("420000")
    )


def test_parse_ctc_lakh_value_10():
    assert (
        parse_ctc("10.0")
        == Decimal("1000000")
    )


def test_parse_ctc_absolute_inr():
    assert (
        parse_ctc("417964")
        == Decimal("417964")
    )


def test_parse_ctc_large_absolute_inr():
    assert (
        parse_ctc("1135514")
        == Decimal("1135514")
    )


def test_parse_ctc_invalid():
    assert parse_ctc("not-a-number") is None


def test_parse_applied_date_iso():
    assert parse_applied_date(
        "2026-07-03"
    ) == date(2026, 7, 3)


def test_parse_applied_date_dash():
    assert parse_applied_date(
        "15-06-2026"
    ) == date(2026, 6, 15)


def test_parse_applied_date_slash():
    assert parse_applied_date(
        "07/13/2026"
    ) == date(2026, 7, 13)


def test_parse_applied_date_month_name():
    assert parse_applied_date(
        "15 Jul 2026"
    ) == date(2026, 7, 15)


def test_parse_applied_date_single_digit_day():
    assert parse_applied_date(
        "2 Jul 2026"
    ) == date(2026, 7, 2)


def test_parse_applied_date_invalid():
    assert parse_applied_date(
        "not-a-date"
    ) is None