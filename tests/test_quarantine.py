from src.validation.quarantine import (
    build_quarantine_record,
    build_quarantine_records,
)


def test_build_quarantine_record():
    record = build_quarantine_record(
        run_id=10,
        source_name="naukri",
        source_file="source1_naukri_applicants.csv",
        source_row_number=25,
        staging_id=26,
        reason_code="INVALID_EMAIL",
        reason_detail="INVALID_EMAIL; INVALID_PHONE",
        raw_payload={
            "Full Name": "Test Person",
            "Email": "invalid",
        },
    )

    assert record["run_id"] == 10
    assert record["source_name"] == "naukri"
    assert record["source_row_number"] == 25
    assert record["staging_id"] == 26
    assert record["reason_code"] == "INVALID_EMAIL"


def test_build_quarantine_records_skips_valid_rows():
    rows = [
        {
            "source_row_number": 1,
            "staging_id": 10,
            "validation_errors": [],
            "raw_payload": {
                "name": "Valid Person",
            },
        },
        {
            "source_row_number": 2,
            "staging_id": 11,
            "validation_errors": [
                "INVALID_PHONE",
            ],
            "raw_payload": {
                "name": "Invalid Person",
                "phone": "123",
            },
        },
    ]

    records = build_quarantine_records(
        run_id=5,
        source_name="cbnexus",
        source_file="source3_cbnexus_contacts.csv",
        source_rows=rows,
    )

    assert len(records) == 1
    assert records[0]["reason_code"] == "INVALID_PHONE"


def test_multiple_errors_create_one_quarantine_record():
    rows = [
        {
            "source_row_number": 5,
            "staging_id": 15,
            "validation_errors": [
                "INVALID_EMAIL",
                "INVALID_PHONE",
                "INVALID_CTC",
            ],
            "raw_payload": {},
        }
    ]

    records = build_quarantine_records(
        run_id=7,
        source_name="naukri",
        source_file="source1_naukri_applicants.csv",
        source_rows=rows,
    )

    assert len(records) == 1

    assert records[0]["reason_code"] == (
        "INVALID_EMAIL"
    )

    assert records[0]["reason_detail"] == (
        "INVALID_EMAIL; INVALID_PHONE; INVALID_CTC"
    )