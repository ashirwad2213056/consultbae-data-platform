from datetime import datetime
from decimal import Decimal

from src.database.connection import get_connection
from src.ingestion.resolve_identities import (
    normalize_email,
    normalize_phone,
    resolve_all_identities,
)


def get_staging_rows(conn):
    queries = {
        "naukri": """
            SELECT
                staging_id,
                source_row_number,
                source_file,
                full_name,
                email,
                phone,
                city,
                experience_years,
                current_ctc,
                applied_date,
                skills
            FROM staging.naukri_applicants
            ORDER BY staging_id
        """,
        "gig": """
            SELECT
                staging_id,
                source_row_number,
                source_file,
                email_id,
                worker_name,
                rate,
                location,
                status,
                skill_tags
            FROM staging.gig_workers
            ORDER BY staging_id
        """,
        "cbnexus": """
            SELECT
                staging_id,
                source_row_number,
                source_file,
                name,
                phone_number,
                city,
                verified,
                projects_completed
            FROM staging.cbnexus_contacts
            ORDER BY staging_id
        """,
    }

    result = {}

    with conn.cursor() as cur:
        for source, query in queries.items():
            cur.execute(query)

            columns = [
                description.name
                for description in cur.description
            ]

            result[source] = [
                dict(zip(columns, row))
                for row in cur.fetchall()
            ]

    return result


def build_staging_lookup(staging_rows):
    """
    Build a lookup from (source, source_row_number) to the
    staging row dict.

    Both the identity resolver and staging now use the
    physical CSV row number (index + 2), so no offset
    conversion is needed.
    """

    lookup = {}

    for source, rows in staging_rows.items():
        for row in rows:
            lookup[
                (source, row["source_row_number"])
            ] = row

    return lookup


def insert_worker(
    cur,
    worker_id,
    canonical_name,
    email,
    phone,
    city,
):
    cur.execute(
        """
        INSERT INTO core.workers (
            worker_id,
            canonical_name,
            email,
            phone_10,
            canonical_city
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (worker_id)
        DO UPDATE SET
            canonical_name = COALESCE(
                core.workers.canonical_name,
                EXCLUDED.canonical_name
            ),
            email = COALESCE(
                core.workers.email,
                EXCLUDED.email
            ),
            phone_10 = COALESCE(
                core.workers.phone_10,
                EXCLUDED.phone_10
            ),
            canonical_city = COALESCE(
                core.workers.canonical_city,
                EXCLUDED.canonical_city
            ),
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            worker_id,
            canonical_name,
            email,
            phone,
            city,
        ),
    )


def insert_source_record(
    cur,
    worker_id,
    source,
    row,
    result,
):
    cur.execute(
        """
        INSERT INTO core.worker_source_records (
            worker_id,
            source_name,
            source_row_number,
            source_file,
            staging_id,
            match_method,
            confidence
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (
            source_name,
            source_row_number,
            staging_id
        )
        DO NOTHING
        """,
        (
            worker_id,
            source,
            row["source_row_number"],
            row["source_file"],
            row["staging_id"],
            result["match_method"],
            result["confidence"],
        ),
    )


def parse_date(date_str):
    if not date_str:
        return None
    date_str = str(date_str).strip()
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    return date_str


def load_naukri_data(
    cur,
    worker_id,
    row,
):
    cur.execute(
        """
        INSERT INTO core.naukri_worker_data (
            worker_id,
            staging_id,
            experience_years,
            current_ctc,
            applied_date
        )
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1
            FROM core.naukri_worker_data
            WHERE worker_id = %s
              AND staging_id = %s
        )
        """,
        (
            worker_id,
            row["staging_id"],
            row["experience_years"],
            row["current_ctc"],
            parse_date(row["applied_date"]),
            worker_id,
            row["staging_id"],
        ),
    )


def parse_gig_rate(rate):
    if not rate:
        return None, None

    value = str(rate).strip().lower()

    if "/hr" in value:
        amount = value.replace("/hr", "").strip()
        return Decimal(amount), "HOUR"

    if "/month" in value:
        amount = value.replace("/month", "").strip()
        return Decimal(
            amount.replace("k", "")
        ) * Decimal("1000"), "MONTH"

    return None, None


def load_gig_data(
    cur,
    worker_id,
    row,
):
    rate_amount, rate_unit = parse_gig_rate(
        row["rate"]
    )

    cur.execute(
        """
        INSERT INTO core.gig_worker_data (
            worker_id,
            staging_id,
            rate_amount,
            rate_unit,
            status
        )
        SELECT %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1
            FROM core.gig_worker_data
            WHERE worker_id = %s
              AND staging_id = %s
        )
        """,
        (
            worker_id,
            row["staging_id"],
            rate_amount,
            rate_unit,
            row["status"],
            worker_id,
            row["staging_id"],
        ),
    )


def parse_boolean(value):
    if value is None:
        return None

    normalized = str(value).strip().lower()

    if normalized in {"yes", "y", "true", "1"}:
        return True

    if normalized in {"no", "n", "false", "0"}:
        return False

    return None


def load_cbnexus_data(
    cur,
    worker_id,
    row,
):
    cur.execute(
        """
        INSERT INTO core.cbnexus_worker_data (
            worker_id,
            staging_id,
            verified,
            projects_completed
        )
        SELECT %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1
            FROM core.cbnexus_worker_data
            WHERE worker_id = %s
              AND staging_id = %s
        )
        """,
        (
            worker_id,
            row["staging_id"],
            parse_boolean(row["verified"]),
            row["projects_completed"],
            worker_id,
            row["staging_id"],
        ),
    )


def load_core():
    results = resolve_all_identities()

    if isinstance(results, tuple):
        identity_results = results[3]
    else:
        identity_results = results

    conn = get_connection()

    try:
        staging_rows = get_staging_rows(conn)

        staging_lookup = build_staging_lookup(
            staging_rows
        )

        with conn.transaction():
            with conn.cursor() as cur:

                # Wipe existing core database structures
                cur.execute("TRUNCATE TABLE core.workers CASCADE;")

                for result in identity_results.to_dict(
                    orient="records"
                ):
                    worker_id = result["worker_id"]
                    source = result["source"]
                    source_row = result["source_row"]

                    staging_row = staging_lookup[
                        (source, source_row)
                    ]

                    if source == "naukri":
                        name = staging_row["full_name"]
                        email = normalize_email(
                            staging_row["email"]
                        )
                        phone = normalize_phone(
                            staging_row["phone"]
                        )
                        city = staging_row["city"]

                    elif source == "gig":
                        name = staging_row["worker_name"]
                        email = normalize_email(
                            staging_row["email_id"]
                        )
                        phone = None
                        city = staging_row["location"]

                    else:
                        name = staging_row["name"]
                        email = None
                        phone = normalize_phone(
                            staging_row["phone_number"]
                        )
                        city = staging_row["city"]

                    insert_worker(
                        cur,
                        worker_id,
                        name,
                        email,
                        phone,
                        city,
                    )

                    insert_source_record(
                        cur,
                        worker_id,
                        source,
                        staging_row,
                        result,
                    )

                    if source == "naukri":
                        load_naukri_data(
                            cur,
                            worker_id,
                            staging_row,
                        )

                    elif source == "gig":
                        load_gig_data(
                            cur,
                            worker_id,
                            staging_row,
                        )

                    elif source == "cbnexus":
                        load_cbnexus_data(
                            cur,
                            worker_id,
                            staging_row,
                        )

        conn.commit()
        return len(identity_results)

    finally:
        conn.close()


if __name__ == "__main__":
    count = load_core()

    print(
        f"Loaded {count} resolved source records."
    )
