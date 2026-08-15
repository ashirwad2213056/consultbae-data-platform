from pathlib import Path

import pandas as pd

from src.database.connection import get_connection


RAW_DIR = Path("data/raw")

PIPELINE_NAME = "source_staging_ingestion"

SOURCES = {
    "naukri": {
        "file": "source1_naukri_applicants.csv",
    },
    "gig": {
        "file": "source2_gig_workers.csv",
    },
    "cbnexus": {
        "file": "source3_cbnexus_contacts.csv",
    },
}


def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename

    return pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
    )


def create_pipeline_run(conn) -> int:
    sql = """
        INSERT INTO audit.pipeline_runs (
            pipeline_name,
            status
        )
        VALUES (
            %s,
            'RUNNING'
        )
        RETURNING run_id;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (PIPELINE_NAME,),
        )

        return cursor.fetchone()[0]


def update_pipeline_success(
    conn,
    run_id: int,
    records_received: int,
    records_processed: int,
    records_rejected: int,
) -> None:

    sql = """
        UPDATE audit.pipeline_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = 'SUCCESS',
            records_received = %s,
            records_processed = %s,
            records_rejected = %s
        WHERE run_id = %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                records_received,
                records_processed,
                records_rejected,
                run_id,
            ),
        )


def update_pipeline_failed(
    conn,
    run_id: int,
    records_received: int,
    records_processed: int,
    records_rejected: int,
    error_message: str,
) -> None:

    sql = """
        UPDATE audit.pipeline_runs
        SET
            completed_at = CURRENT_TIMESTAMP,
            status = 'FAILED',
            records_received = %s,
            records_processed = %s,
            records_rejected = %s,
            error_message = %s
        WHERE run_id = %s;
    """

    with conn.cursor() as cursor:
        cursor.execute(
            sql,
            (
                records_received,
                records_processed,
                records_rejected,
                error_message[:5000],
                run_id,
            ),
        )


def clear_previous_snapshot(
    conn,
    source_file: str,
) -> None:

    tables = [
        "staging.naukri_applicants",
        "staging.gig_workers",
        "staging.cbnexus_contacts",
    ]

    for table in tables:

        sql = f"""
            DELETE FROM {table}
            WHERE source_file = %s;
        """

        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (source_file,),
            )


def insert_naukri(
    conn,
    dataframe: pd.DataFrame,
    source_file: str,
    run_id: int,
) -> tuple[int, int]:

    sql = """
        INSERT INTO staging.naukri_applicants (
            full_name,
            email,
            phone,
            city,
            experience_years,
            current_ctc,
            applied_date,
            skills,
            source_file,
            source_row_number,
            run_id
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        );
    """

    received = len(dataframe)
    processed = 0

    with conn.cursor() as cursor:

        for index, row in dataframe.iterrows():

            cursor.execute(
                sql,
                (
                    row["Full Name"],
                    row["Email"],
                    row["Phone"],
                    row["City"],
                    row["Experience (Years)"],
                    row["Current CTC"],
                    row["Applied Date"],
                    row["Skills"],
                    source_file,
                    index + 2,
                    run_id,
                ),
            )

            processed += 1

    return received, processed


def insert_gig(
    conn,
    dataframe: pd.DataFrame,
    source_file: str,
    run_id: int,
) -> tuple[int, int]:

    sql = """
        INSERT INTO staging.gig_workers (
            email_id,
            worker_name,
            rate,
            location,
            status,
            skill_tags,
            source_file,
            source_row_number,
            run_id
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        );
    """

    received = len(dataframe)
    processed = 0

    with conn.cursor() as cursor:

        for index, row in dataframe.iterrows():

            # Completely blank source row.
            if all(
                value.strip() == ""
                for value in row
            ):
                continue

            cursor.execute(
                sql,
                (
                    row["email_id"],
                    row["worker_name"],
                    row["rate"],
                    row["location"],
                    row["status"],
                    row["skill_tags"],
                    source_file,
                    index + 2,
                    run_id,
                ),
            )

            processed += 1

    return received, processed


def insert_cbnexus(
    conn,
    dataframe: pd.DataFrame,
    source_file: str,
    run_id: int,
) -> tuple[int, int]:

    sql = """
        INSERT INTO staging.cbnexus_contacts (
            name,
            phone_number,
            city,
            verified,
            projects_completed,
            source_file,
            source_row_number,
            run_id
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        );
    """

    received = len(dataframe)
    processed = 0

    with conn.cursor() as cursor:

        for index, row in dataframe.iterrows():

            # Repeated header is not a contact.
            if (
                row["Name"]
                .strip()
                .lower()
                == "name"
            ):
                continue

            cursor.execute(
                sql,
                (
                    row["Name"],
                    row["Phone Number"],
                    row["City"],
                    row["Verified"],
                    row["Projects Completed"],
                    source_file,
                    index + 2,
                    run_id,
                ),
            )

            processed += 1

    return received, processed


def main():

    print("=" * 100)
    print("AUDITED CSV → POSTGRESQL STAGING INGESTION")
    print("=" * 100)

    conn = get_connection()

    run_id = None

    records_received = 0
    records_processed = 0
    records_rejected = 0

    try:

        # --------------------------------------------------
        # Create the audit run first.
        #
        # This transaction is committed independently so
        # that a later staging failure can still be recorded.
        # --------------------------------------------------

        run_id = create_pipeline_run(conn)

        conn.commit()

        print(
            f"\nPipeline run created: {run_id}"
        )

        # --------------------------------------------------
        # Load source files.
        # --------------------------------------------------

        naukri = load_csv(
            SOURCES["naukri"]["file"]
        )

        gig = load_csv(
            SOURCES["gig"]["file"]
        )

        cbnexus = load_csv(
            SOURCES["cbnexus"]["file"]
        )

        # Physical source records received.
        records_received = (
            len(naukri)
            + len(gig)
            + len(cbnexus)
        )

        # --------------------------------------------------
        # Replace previous snapshot.
        # --------------------------------------------------

        clear_previous_snapshot(
            conn,
            SOURCES["naukri"]["file"],
        )

        clear_previous_snapshot(
            conn,
            SOURCES["gig"]["file"],
        )

        clear_previous_snapshot(
            conn,
            SOURCES["cbnexus"]["file"],
        )

        # --------------------------------------------------
        # Insert Naukri.
        # --------------------------------------------------

        _, processed = insert_naukri(
            conn,
            naukri,
            SOURCES["naukri"]["file"],
            run_id,
        )

        records_processed += processed

        print(
            f"Naukri: {processed} rows processed"
        )

        # --------------------------------------------------
        # Insert Gig.
        # --------------------------------------------------

        _, processed = insert_gig(
            conn,
            gig,
            SOURCES["gig"]["file"],
            run_id,
        )

        records_processed += processed

        print(
            f"Gig: {processed} rows processed"
        )

        # --------------------------------------------------
        # Insert CBNexus.
        # --------------------------------------------------

        _, processed = insert_cbnexus(
            conn,
            cbnexus,
            SOURCES["cbnexus"]["file"],
            run_id,
        )

        records_processed += processed

        print(
            f"CBNexus: {processed} rows processed"
        )

        records_rejected = (
            records_received
            - records_processed
        )

        # --------------------------------------------------
        # Update audit record and commit the whole staging
        # snapshot atomically.
        # --------------------------------------------------

        update_pipeline_success(
            conn,
            run_id,
            records_received,
            records_processed,
            records_rejected,
        )

        conn.commit()

        print("\n" + "-" * 100)

        print(
            f"Run ID            : {run_id}"
        )

        print(
            f"Records received  : {records_received}"
        )

        print(
            f"Records processed : {records_processed}"
        )

        print(
            f"Records rejected  : {records_rejected}"
        )

        print(
            "Status            : SUCCESS"
        )

    except Exception as exc:

        # Roll back staging changes.
        conn.rollback()

        if run_id is not None:

            try:

                update_pipeline_failed(
                    conn,
                    run_id,
                    records_received,
                    records_processed,
                    records_rejected,
                    str(exc),
                )

                conn.commit()

            except Exception:

                conn.rollback()

        print("\n" + "-" * 100)

        print(
            f"Run ID: {run_id}"
        )

        print(
            "Status: FAILED"
        )

        print(
            f"Error: {exc}"
        )

        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()