CREATE TABLE IF NOT EXISTS core.workers (
    worker_id VARCHAR(20) PRIMARY KEY,

    canonical_name TEXT,

    email TEXT,

    phone_10 VARCHAR(10),

    canonical_city TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT workers_phone_10_check
        CHECK (
            phone_10 IS NULL
            OR phone_10 ~ '^[0-9]{10}$'
        )
);


CREATE TABLE IF NOT EXISTS core.worker_source_records (
    worker_source_id BIGSERIAL PRIMARY KEY,

    worker_id VARCHAR(20) NOT NULL,

    source_name VARCHAR(30) NOT NULL,

    source_row_number INTEGER NOT NULL,

    source_file TEXT NOT NULL,

    staging_id BIGINT,

    match_method VARCHAR(30) NOT NULL,

    confidence VARCHAR(20) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_worker_source_worker
        FOREIGN KEY (worker_id)
        REFERENCES core.workers(worker_id),

    CONSTRAINT worker_source_source_check
        CHECK (
            source_name IN ('naukri', 'gig', 'cbnexus')
        ),

    CONSTRAINT worker_source_confidence_check
        CHECK (
            confidence IN ('BASE', 'HIGH', 'REVIEW')
        )
);


CREATE TABLE IF NOT EXISTS core.naukri_worker_data (
    worker_id VARCHAR(20) PRIMARY KEY,

    staging_id BIGINT NOT NULL,

    experience_years NUMERIC(5,2),

    current_ctc NUMERIC(15,2),

    applied_date DATE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_naukri_worker
        FOREIGN KEY (worker_id)
        REFERENCES core.workers(worker_id)
);


CREATE TABLE IF NOT EXISTS core.gig_worker_data (
    worker_id VARCHAR(20) PRIMARY KEY,

    staging_id BIGINT NOT NULL,

    rate_amount NUMERIC(15,2),

    rate_unit VARCHAR(20),

    status VARCHAR(20),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_gig_worker
        FOREIGN KEY (worker_id)
        REFERENCES core.workers(worker_id),

    CONSTRAINT gig_rate_unit_check
        CHECK (
            rate_unit IS NULL
            OR rate_unit IN ('HOUR', 'MONTH')
        )
);


CREATE TABLE IF NOT EXISTS core.cbnexus_worker_data (
    worker_id VARCHAR(20) PRIMARY KEY,

    staging_id BIGINT NOT NULL,

    verified BOOLEAN,

    projects_completed INTEGER,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cbnexus_worker
        FOREIGN KEY (worker_id)
        REFERENCES core.workers(worker_id)
);


CREATE TABLE IF NOT EXISTS core.skills (
    skill_id BIGSERIAL PRIMARY KEY,

    skill_name TEXT NOT NULL UNIQUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS core.worker_skills (
    worker_id VARCHAR(20) NOT NULL,

    skill_id BIGINT NOT NULL,

    source_name VARCHAR(30) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (worker_id, skill_id, source_name),

    CONSTRAINT fk_worker_skills_worker
        FOREIGN KEY (worker_id)
        REFERENCES core.workers(worker_id),

    CONSTRAINT fk_worker_skills_skill
        FOREIGN KEY (skill_id)
        REFERENCES core.skills(skill_id),

    CONSTRAINT worker_skills_source_check
        CHECK (
            source_name IN ('naukri', 'gig', 'cbnexus')
        )
);