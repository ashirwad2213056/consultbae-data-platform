CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,

    pipeline_name VARCHAR(100) NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',

    records_received INTEGER NOT NULL DEFAULT 0,

    records_processed INTEGER NOT NULL DEFAULT 0,

    records_rejected INTEGER NOT NULL DEFAULT 0,

    records_quarantined INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pipeline_runs_status_check
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
);