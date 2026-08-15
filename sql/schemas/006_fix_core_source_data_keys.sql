-- Source-specific core tables represent source observations,
-- not unique workers. Therefore worker_id must not be their
-- primary key.

ALTER TABLE core.naukri_worker_data
    DROP CONSTRAINT IF EXISTS naukri_worker_data_pkey;

ALTER TABLE core.naukri_worker_data
    ADD COLUMN IF NOT EXISTS naukri_data_id BIGSERIAL;

ALTER TABLE core.naukri_worker_data
    ADD CONSTRAINT naukri_worker_data_pkey
    PRIMARY KEY (naukri_data_id);


ALTER TABLE core.gig_worker_data
    DROP CONSTRAINT IF EXISTS gig_worker_data_pkey;

ALTER TABLE core.gig_worker_data
    ADD COLUMN IF NOT EXISTS gig_data_id BIGSERIAL;

ALTER TABLE core.gig_worker_data
    ADD CONSTRAINT gig_worker_data_pkey
    PRIMARY KEY (gig_data_id);


ALTER TABLE core.cbnexus_worker_data
    DROP CONSTRAINT IF EXISTS cbnexus_worker_data_pkey;

ALTER TABLE core.cbnexus_worker_data
    ADD COLUMN IF NOT EXISTS cbnexus_data_id BIGSERIAL;

ALTER TABLE core.cbnexus_worker_data
    ADD CONSTRAINT cbnexus_worker_data_pkey
    PRIMARY KEY (cbnexus_data_id);