import json


def build_quarantine_record(
    *,
    run_id,
    source_name,
    source_file,
    source_row_number,
    staging_id,
    reason_code,
    reason_detail,
    raw_payload,
):
    return {
        "run_id": run_id,
        "source_name": source_name,
        "source_file": source_file,
        "source_row_number": source_row_number,
        "staging_id": staging_id,
        "reason_code": reason_code,
        "reason_detail": reason_detail,
        "raw_payload": raw_payload,
    }


def build_quarantine_records(
    *,
    run_id,
    source_name,
    source_file,
    source_rows,
):
    """
    Convert validation failures into records suitable
    for audit.quarantined_records.

    source_rows must contain:
        source_row_number
        staging_id
        validation_errors
        raw_payload
    """

    quarantined = []

    for row in source_rows:
        errors = row.get("validation_errors", [])

        if not errors:
            continue

        reason_code = errors[0]

        reason_detail = "; ".join(errors)

        quarantined.append(
            build_quarantine_record(
                run_id=run_id,
                source_name=source_name,
                source_file=source_file,
                source_row_number=row.get(
                    "source_row_number"
                ),
                staging_id=row.get(
                    "staging_id"
                ),
                reason_code=reason_code,
                reason_detail=reason_detail,
                raw_payload=row.get(
                    "raw_payload",
                    {},
                ),
            )
        )

    return quarantined