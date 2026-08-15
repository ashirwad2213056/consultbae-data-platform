-- CREATE TABLE IF NOT EXISTS staging.naukri_applicants (
--     staging_id BIGSERIAL PRIMARY KEY,

--     full_name TEXT,
--     email TEXT,
--     phone TEXT,
--     city TEXT,
--     experience_years TEXT,
--     current_ctc TEXT,
--     applied_date TEXT,
--     skills TEXT,

--     source_file TEXT NOT NULL,
--     source_row_number INTEGER NOT NULL,

--     ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );


-- CREATE TABLE IF NOT EXISTS staging.gig_workers (
--     staging_id BIGSERIAL PRIMARY KEY,

--     email_id TEXT,
--     worker_name TEXT,
--     rate TEXT,
--     location TEXT,
--     status TEXT,
--     skill_tags TEXT,

--     source_file TEXT NOT NULL,
--     source_row_number INTEGER NOT NULL,

--     ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );


-- CREATE TABLE IF NOT EXISTS staging.cbnexus_contacts (
--     staging_id BIGSERIAL PRIMARY KEY,

--     name TEXT,
--     phone_number TEXT,
--     city TEXT,
--     verified TEXT,
--     projects_completed TEXT,

--     source_file TEXT NOT NULL,
--     source_row_number INTEGER NOT NULL,

--     ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE IF NOT EXISTS staging.naukri_applicants (
    staging_id BIGSERIAL PRIMARY KEY,

    full_name TEXT,
    email TEXT,
    phone TEXT,
    city TEXT,
    experience_years TEXT,
    current_ctc TEXT,
    applied_date TEXT,
    skills TEXT,

    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,

    run_id BIGINT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_naukri_pipeline_run
        FOREIGN KEY (run_id)
        REFERENCES audit.pipeline_runs(run_id)
);


CREATE TABLE IF NOT EXISTS staging.gig_workers (
    staging_id BIGSERIAL PRIMARY KEY,

    email_id TEXT,
    worker_name TEXT,
    rate TEXT,
    location TEXT,
    status TEXT,
    skill_tags TEXT,

    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,

    run_id BIGINT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_gig_pipeline_run
        FOREIGN KEY (run_id)
        REFERENCES audit.pipeline_runs(run_id)
);


CREATE TABLE IF NOT EXISTS staging.cbnexus_contacts (
    staging_id BIGSERIAL PRIMARY KEY,

    name TEXT,
    phone_number TEXT,
    city TEXT,
    verified TEXT,
    projects_completed TEXT,

    source_file TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,

    run_id BIGINT,

    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cbnexus_pipeline_run
        FOREIGN KEY (run_id)
        REFERENCES audit.pipeline_runs(run_id)
);