ALTER TABLE core.worker_source_records
    ADD CONSTRAINT uq_worker_source_observation
    UNIQUE (
        source_name,
        source_row_number,
        staging_id
    );