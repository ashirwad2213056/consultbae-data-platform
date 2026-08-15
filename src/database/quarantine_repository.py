import json


def insert_quarantine_records(
    conn,
    records,
):
    if not records:
        return 0

    query = """
        INSERT INTO audit.quarantined_records (
            run_id,
            source_name,
            source_file,
            source_row_number,
            staging_id,
            reason_code,
            reason_detail,
            raw_payload
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    inserted = 0

    with conn.cursor() as cur:
        for record in records:
            cur.execute(
                query,
                (
                    record["run_id"],
                    record["source_name"],
                    record["source_file"],
                    record["source_row_number"],
                    record["staging_id"],
                    record["reason_code"],
                    record["reason_detail"],
                    json.dumps(
                        record["raw_payload"]
                    ),
                ),
            )

            inserted += 1

    return inserted
    