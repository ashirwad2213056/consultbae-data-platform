CREATE TABLE IF NOT EXISTS core.audio_submissions (
    submission_id BIGSERIAL PRIMARY KEY,
    worker_id VARCHAR(20) NOT NULL REFERENCES core.workers(worker_id),
    file_path TEXT NOT NULL,
    duration_seconds NUMERIC,
    sample_rate_hz INTEGER,
    bitrate_kbps INTEGER,
    loudness_db NUMERIC,
    submitted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
