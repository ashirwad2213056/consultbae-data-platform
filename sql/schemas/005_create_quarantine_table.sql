CREATE TABLE IF NOT EXISTS audit.quarantined_records (
    quarantine_id BIGSERIAL PRIMARY KEY,

    run_id BIGINT NOT NULL,

    source_name VARCHAR(30) NOT NULL,

    source_file TEXT NOT NULL,

    source_row_number INTEGER,

    staging_id BIGINT,

    reason_code VARCHAR(50) NOT NULL,

    reason_detail TEXT,

    raw_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quarantine_pipeline_run
        FOREIGN KEY (run_id)
        REFERENCES audit.pipeline_runs(run_id),

    CONSTRAINT quarantine_source_check
        CHECK (
            source_name IN ('naukri', 'gig', 'cbnexus')
        )
);