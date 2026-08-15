# ConsultBae AI Automation Assignment
## Data Analytics, Data Quality & Proposed Database Model

**Version:** Analytics & Data Model v1.0  
**Database:** PostgreSQL

---

## 1. Executive Summary

The ConsultBae assignment provides three CSV datasets originating from different internal systems. The objective is to merge these systems into one clean, consistent database while ensuring that the **same real-world worker appearing in multiple systems becomes one worker record**.

The three datasets contain overlapping people, inconsistent data, and no single common ID across all files. Therefore, entity resolution is a central part of the solution.

Our proposed architecture is:

```text
                         WORKER IDENTITY
                              |
             Global WorkerID / Canonical Identity
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
      Naukri Profile      Gig Profile      CBNexus Profile
```

The key design decision is:

> **`WorkerID` is the global identifier and the relationship key between the worker and profile tables.**

`WorkerName` is retained in the profile tables for human readability, but it is **not used as a foreign key**.

The database will use PostgreSQL and will be organized into:

```text
raw
staging
core
audit
```

Pipeline:

```text
Raw Data
   ↓
Structural Validation
   ↓
Normalization
   ↓
Semantic Validation
   ↓
Entity Resolution
   ↓
Canonical WorkerID
   ↓
Core Database
   ↓
Audit / Data Quality Reporting
```

---

# 2. Assignment Context

The three source datasets represent different systems:

| Source | Business purpose | Proposed profile |
|---|---|---|
| CSV-1 | Naukri/recruitment applicant data | `NaukriProfile` |
| CSV-2 | Gig-worker information | `GigProfile` |
| CSV-3 | CBNexus contacts | `CBNexusProfile` |

The source systems contain overlapping workers.

The challenge is therefore not simply:

```text
CSV 1 + CSV 2 + CSV 3
```

but:

```text
Different source records
        ↓
Determine which records represent
the same real-world worker
        ↓
Generate one global WorkerID
        ↓
Attach source-specific information
```

---

# 3. Analytics Objectives

Our analysis focused on:

1. Data quality
2. Data normalization
3. Cross-source relationships
4. Entity resolution
5. Database design

The objective was to understand the source data before implementing the pipeline.

---

# 4. Data Quality Findings

## 4.1 Name Inconsistencies

Observed problems include variations in capitalization and formatting.

Examples:

```text
RAHUL CHOPRA
Rahul Chopra
rahul chopra
RaHuL cHoPrA
```

Canonical format:

```text
Aa / Title Case
```

Example:

```text
RAHUL CHOPRA
      ↓
Rahul Chopra
```

Rules:

- trim leading/trailing whitespace;
- collapse unnecessary spaces;
- normalize capitalization;
- preserve meaningful punctuation;
- never use name as the primary key.

---

## 4.2 Email Irregularities

Email addresses appear in different capitalization formats.

Example:

```text
ISHA.CHOPRA95@MAILTEST.EXAMPLE.ORG
```

Canonical:

```text
isha.chopra95@mailtest.example.org
```

Rules:

- trim;
- lowercase;
- validate basic syntax;
- retain source value for audit when transformed.

A synthetic/test-looking domain is not automatically invalid solely because it looks synthetic.

---

## 4.3 Phone Number Irregularities

Phone numbers occur in different representations involving:

- `+91`;
- `91`;
- `0`;
- spaces;
- hyphens;
- plain digits.

Canonical representation:

```text
9000000295
```

Exactly:

```text
10 digits
```

Examples:

```text
+91-9000000295 -> 9000000295
919000000295   -> 9000000295
09000000295    -> 9000000295
```

Invalid/unresolvable numbers should be flagged or quarantined.

---

## 4.4 Location Irregularities

Location values have formatting and capitalization differences.

Examples:

```text
PUNE
pune
Pune
```

Canonical:

```text
Pune
```

Controlled aliases may be used:

```text
Bangalore -> Bengaluru
Gurgaon   -> Gurugram
```

Geographically related values should not automatically be merged without an explicit business rule.

---

## 4.5 Skills Irregularities

The same person can have overlapping/common skills across multiple source files.

Example:

```text
Naukri:
Python, React, MongoDB

Gig:
Python, React, MongoDB
```

Canonical consolidated set:

```text
Python, React, MongoDB
```

Rules:

- trim;
- normalize capitalization;
- remove duplicates;
- preserve meaningful multi-word skills.

For this assignment, skills can remain in Worker Identity as a normalized consolidated field. A separate `Skill` / `WorkerSkill` model can be introduced later if needed.

---

## 4.6 Work Experience

Canonical type:

```text
DECIMAL
```

Unit:

```text
years
```

Examples:

```text
4.2
3.5
3.0
```

Do not store:

```text
"4.2 years"
```

as free text in the canonical table.

---

## 4.7 CTC Irregularities

The recruitment data contains mixed CTC representations.

Examples:

```text
4.2
8.3
11.2
```

alongside values resembling absolute INR amounts:

```text
417964
775670
1195422
```

The field therefore requires semantic interpretation, not just formatting.

Proposed canonical field:

```text
current_ctc_inr
```

Example where the source value is interpreted as LPA:

```text
4.2 LPA
    ↓
420000 INR
```

The interpretation rule must be documented, and the original source value retained for auditability.

---

## 4.8 Date Irregularities

Potential source formats include:

```text
DD-MM-YYYY
YYYY-MM-DD
MM/DD/YYYY
DD Mon YYYY
```

Canonical database type:

```text
DATE
```

Canonical representation:

```text
YYYY-MM-DD
```

Date parsing should be source-aware for ambiguous formats.

---

## 4.9 Gig Rate Irregularities

Gig rates can appear in mixed representations:

```text
1415/hr
15k/month
```

Instead of one free-text field, use:

```text
rate_amount
rate_unit
```

Examples:

```text
1415/hr
->
rate_amount = 1415
rate_unit = HOUR
```

```text
15k/month
->
rate_amount = 15000
rate_unit = MONTH
```

---

## 4.10 Status Irregularities

Canonical allowed values:

```text
ACTIVE
INACTIVE
PAUSED
```

Case differences are normalized.

A value that belongs to another semantic field, such as a location appearing in the status column, is a semantic/structural problem and should be flagged rather than silently converted.

---

## 4.11 CBNexus `Verified` Irregularities

The dataset uses different representations:

```text
Y
N
Yes
No
yes
no
```

Canonical type:

```text
BOOLEAN
```

Mapping:

```text
Y / Yes / yes -> TRUE
N / No / no   -> FALSE
```

Unknown values should be flagged.

---

## 4.12 Projects Completed

Canonical type:

```text
INTEGER
```

Validation:

```text
projects_completed >= 0
```

---

# 5. Structural Data Problems

In addition to field-level formatting problems, the datasets contain structural irregularities.

## Blank Rows

Some records contain empty rows.

## Repeated Headers

The third CSV contains headers repeated in the middle of the dataset.

Conceptually:

```text
Name | Phone | City | Verified
Rahul | ...
Isha  | ...
Name | Phone | City | Verified   <- repeated header
Amit  | ...
```

The repeated header should be detected and excluded from normal processing while the raw source remains preserved.

## Column Shifts

Some records contain values appearing under the wrong field/column.

For example:

```text
Location column <- status-like value
```

This is more serious than capitalization because it can create semantic corruption.

---

# 6. Blank vs Missing vs Invalid

We should distinguish:

### Missing

```text
NULL
```

No value supplied.

### Empty

```text
""
```

Blank value supplied.

### Invalid

A value exists but does not satisfy the field's business rules.

Example:

```text
status = "Pune"
```

### Normalized

A valid source value transformed into canonical form.

Example:

```text
"yes" -> TRUE
```

This distinction will be used in audit reporting.

---

# 7. Cross-Source Entity Relationship

The three source systems do not provide one universal identifier.

Therefore:

```text
Naukri Worker
       +
Gig Worker
       +
CBNexus Contact
```

cannot simply be joined using a source-provided ID.

We need an internally generated:

# `WorkerID`

This becomes the global identifier.

---

# 8. Why WorkerID Is Necessary

A worker can appear in multiple systems with variations in name, email, phone and formatting.

Conceptually:

```text
CSV-1
Isha Chopra
isha.chopra95@example.org
09000000295

CSV-2
ISHA.CHOPRA95@EXAMPLE.ORG
Isha Chopra
+91-9000000295

CSV-3
ISHA CHOPRA
+91-9000000295
```

All should map to:

```text
W000001
```

rather than creating three independent workers.

---

# 9. Entity Resolution Strategy

Proposed matching hierarchy:

```text
1. Exact normalized email
            ↓
2. Exact normalized phone
            ↓
3. Strong attribute combinations
            ↓
4. Fuzzy candidate matching
            ↓
5. Manual/quarantine decision
```

Strong combinations include:

```text
Name + Phone
Name + Email
Name + Phone + Location
```

### Critical rule

Never merge workers using name alone.

Names are not guaranteed to be unique.

---

# 10. Matching Confidence

Use:

```text
HIGH
MEDIUM
LOW
UNMATCHED
```

Examples:

| Match evidence | Confidence |
|---|---|
| Exact normalized email | HIGH |
| Exact normalized phone | HIGH |
| Name + phone | HIGH |
| Name + email | HIGH |
| Name + location | MEDIUM |
| Name only | LOW |

Low-confidence matches should not be automatically merged.

---

# 11. Final Proposed Database Model

The core database contains four business tables.

```text
                         WORKER IDENTITY
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
      Naukri Profile      Gig Profile      CBNexus Profile
```

---

# 12. Table 1 — Worker Identity

### `core.worker_identity`

This is the main global table.

| Column | Purpose |
|---|---|
| `WorkerID` | Global Primary Key |
| `WorkerName` | Canonical worker name |
| `Email` | Normalized email |
| `Phone` | Canonical phone |
| `Location` | Canonical location |
| `Skills` | Consolidated normalized skills |

Conceptually:

```text
WorkerIdentity
-------------------------
WorkerID       PK
WorkerName
Email
Phone
Location
Skills
```

---

# 13. Table 2 — Naukri Profile

### `core.naukri_profile`

Contains recruitment-specific information.

```text
NaukriProfile
-------------------------
WorkerID              PK/FK
WorkerName
WorkExperienceYears
CTC_INR
AppliedDate
```

Relationship:

```text
WorkerIdentity
      |
      | WorkerID
      v
NaukriProfile
```

Cardinality:

```text
1 : 0..1
```

A worker may exist without having a Naukri profile.

---

# 14. Table 3 — Gig Profile

### `core.gig_profile`

Contains gig-worker-specific information.

```text
GigProfile
-------------------------
WorkerID              PK/FK
WorkerName
RateAmount
RateUnit
Status
```

Example:

```text
W000001
Isha Chopra
1415
HOUR
ACTIVE
```

---

# 15. Table 4 — CBNexus Profile

### `core.cbnexus_profile`

Contains CBNexus-specific information.

```text
CBNexusProfile
-------------------------
WorkerID              PK/FK
WorkerName
Verified
ProjectsCompleted
```

Example:

```text
W000001
Isha Chopra
TRUE
6
```

---

# 16. Final ER Model

```text
                         +------------------------+
                         |    WORKER IDENTITY     |
                         +------------------------+
                         | WorkerID        PK     |
                         | WorkerName             |
                         | Email                  |
                         | Phone                  |
                         | Location               |
                         | Skills                 |
                         +-----------+------------+
                                     |
                  +------------------+------------------+
                  |                  |                  |
                  | WorkerID         | WorkerID         | WorkerID
                  |                  |                  |
                  v                  v                  v
       +------------------+ +------------------+ +------------------+
       |  NAUKRI PROFILE  | |   GIG PROFILE    | | CBNEXUS PROFILE  |
       +------------------+ +------------------+ +------------------+
       | WorkerID PK/FK   | | WorkerID PK/FK   | | WorkerID PK/FK   |
       | WorkerName       | | WorkerName       | | WorkerName       |
       | Experience       | | RateAmount       | | Verified         |
       | CTC_INR          | | RateUnit         | | ProjectsCompleted|
       | AppliedDate      | | Status           | |                  |
       +------------------+ +------------------+ +------------------+
```

---

# 17. Why WorkerName Exists in All Four Tables

`WorkerName` is retained in profile tables for readability.

Example:

```text
WorkerID | WorkerName   | CTC
W000001  | Isha Chopra  | 420000
```

However:

```text
WorkerID = relationship key
WorkerName = readable attribute
```

The actual foreign-key relationship is:

```text
NaukriProfile.WorkerID
        ↓
WorkerIdentity.WorkerID
```

WorkerName is not used as the relationship key.

---

# 18. Supporting Audit Tables

The four core business tables are supported by technical/audit tables.

## `audit.import_batch`

Tracks each ingestion:

```text
batch_id
source_system
file_name
file_hash
started_at
completed_at
status
total_rows
valid_rows
rejected_rows
```

Purpose:

- file version tracking;
- reproducibility;
- idempotency;
- batch monitoring.

---

## `audit.worker_source_mapping`

Tracks source provenance:

```text
mapping_id
WorkerID
source_system
source_record_id
source_row_number
```

Example:

```text
W000001 -> NAUKRI -> row 7
W000001 -> GIG -> row 12
W000001 -> CBNEXUS -> row 18
```

This answers:

> Where did this WorkerID come from?

---

## `audit.data_quality_issue`

Conceptually:

```text
issue_id
batch_id
source_system
source_row_number
field_name
issue_type
original_value
normalized_value
action_taken
severity
created_at
```

Example:

```text
Source: CBNEXUS
Row: 17
Field: Verified

Original:
"yes"

Normalized:
TRUE

Issue:
BOOLEAN_FORMAT_NORMALIZED

Action:
TRANSFORMED
```

---

# 19. PostgreSQL Layer Architecture

```text
                    PostgreSQL
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
      RAW            STAGING            CORE
        |                |                |
 source data       cleaned data     final workers
                                      /    |                                         /     |                                     Naukri    Gig   CBNexus

                         AUDIT
                           |
              +------------+-------------+
              |                          |
        Import Batches             Data Quality
              |                          |
        Source Mapping             Transformations
```

---

# 20. Raw Layer

Purpose:

> Preserve exactly what arrived.

Raw data should not be cleaned.

Example:

```text
Source:
ISHA.CHOPRA95@EXAMPLE.COM

RAW:
ISHA.CHOPRA95@EXAMPLE.COM
```

not:

```text
isha.chopra95@example.com
```

The original source value remains available for audit and reproducibility.

---

# 21. Staging Layer

Purpose:

> Clean, normalize and validate data before it reaches the core model.

Example:

```text
RAW
ISHA.CHOPRA95@EXAMPLE.COM
        ↓
STAGING
isha.chopra95@example.com
```

Similarly:

```text
+91-90000000295
        ↓
9000000295
```

and:

```text
yes
        ↓
TRUE
```

---

# 22. Core Layer

Only validated canonical data reaches:

```text
core.worker_identity
core.naukri_profile
core.gig_profile
core.cbnexus_profile
```

This layer should have strong:

- primary keys;
- foreign keys;
- data types;
- constraints;
- indexes.

---

# 23. Audit Layer

Audit records should answer:

```text
What happened?
When?
To which source?
Which row?
Which field?
What was the original value?
What did we change it to?
Why?
```

This makes the pipeline explainable.

---

# 24. Data Processing Lifecycle

```text
             SOURCE CSV
                 |
                 v
          File Validation
                 |
                 v
           Raw Storage
                 |
                 v
       Structural Validation
                 |
                 v
          Normalization
                 |
                 v
      Semantic Validation
                 |
          +------+------+
          |             |
        Valid         Invalid
          |             |
          v             v
   Entity Resolution  Quarantine
          |
          v
      WorkerID
          |
          v
   Canonical Mapping
          |
          v
     Core Database
          |
          v
   Audit + Reporting
```

---

# 25. Data Security Design

Because the datasets contain personal and employment-related information, security controls are part of the architecture.

## Input Security

Validate:

- file type;
- file size;
- expected structure;
- row limits.

## Secrets

Never commit:

```text
.env
database passwords
API keys
n8n credentials
```

## Database Access

Use a restricted application account rather than PostgreSQL superuser credentials.

## Logging

Avoid unnecessary PII exposure.

Prefer:

```text
WorkerID: W000001
Phone: ******0295
Email: is***@example.org
```

## Raw Data

Keep raw data separate and protected.

## Transactions

Core writes should be atomic:

```text
BEGIN
   ↓
Worker
   ↓
Profile
   ↓
COMMIT
```

Failure:

```text
ROLLBACK
```

---

# 26. Idempotency

The pipeline should safely process the same file more than once.

Example:

```text
Run 1:
source.csv
   ↓
W000001 ... W001000
```

Running the same file again should not create duplicate workers.

Use:

```text
file_hash
import_batch
source record identity
WorkerID matching
database constraints
```

Expected:

```text
Run 1 Worker Count
       =
Run 2 Worker Count
```

---

# 27. Error Handling

Use:

```text
SUCCESS
WARNING
REPAIRABLE
REJECTED
FATAL
```

Routing:

```text
                    PROCESS
                       |
             +---------+---------+
             |         |         |
           SUCCESS   WARNING   REJECT
             |         |         |
             v         v         v
            CORE    CORE+AUDIT  QUARANTINE
```

The original raw record is never destroyed.

---

# 28. Future Expansion

The architecture supports future source systems.

For example:

```text
New Source
    ↓
Normalization
    ↓
Entity Resolution
    ↓
Existing WorkerID
```

No separate global identity system is required.

---

# 29. Future Audio Extension

Task 3 can connect directly to the existing Worker model.

Proposed:

```text
AudioSubmission
--------------------------
SubmissionID PK
WorkerID FK
AudioURL
Duration
SampleRate
Bitrate
Loudness
QualityScore
CreatedAt
```

Relationship:

```text
WorkerIdentity
      |
      | 1 : N
      v
AudioSubmission
```

A worker can therefore submit multiple recordings without creating duplicate worker identities.

---

# 30. Scalability Strategy

The architecture should support future growth.

## Batch Processing

Process records in batches instead of loading everything into application memory.

## Database Indexes

Index fields used for identity matching:

```text
normalized email
normalized phone
WorkerID
source identifiers
```

## Transactions

Use transactions for atomic core writes.

## Idempotency

Use import batches and source-record identity.

## Layer Separation

Keep:

```text
raw
staging
core
audit
```

separate.

## Modular Processing

Keep:

```text
ingestion
normalization
validation
matching
transformation
database
```

as separate modules.

---

# 31. Recommended Test Matrix

| Test | Expected |
|---|---|
| Normal record | Accepted |
| Uppercase name | Normalized |
| Uppercase email | Lowercased |
| Mixed phone format | Canonical 10 digits |
| City whitespace | Trimmed |
| City alias | Canonicalized |
| Repeated header | Skipped + audited |
| Blank row | Skipped/rejected + audited |
| Invalid status | Rejected/quarantined |
| Y/Yes | TRUE |
| N/No | FALSE |
| Mixed CTC | Canonical INR |
| Mixed date format | Canonical DATE |
| Same person across files | Same WorkerID |
| Same name, different person | Not automatically merged |
| Same file twice | No duplicate workers |
| DB failure | Transaction rollback |
| Invalid record | Quarantine |
| Future new source | Existing architecture remains usable |

---

# 32. Final Proposed Core Schema

## `core.worker_identity`

```text
WorkerID       PK
WorkerName
Email
Phone
Location
Skills
```

## `core.naukri_profile`

```text
WorkerID       PK/FK
WorkerName
WorkExperience
CTC_INR
AppliedDate
```

## `core.gig_profile`

```text
WorkerID       PK/FK
WorkerName
RateAmount
RateUnit
Status
```

## `core.cbnexus_profile`

```text
WorkerID       PK/FK
WorkerName
Verified
ProjectsCompleted
```

Supporting:

```text
audit.import_batch
audit.worker_source_mapping
audit.data_quality_issue
```

Processing:

```text
raw.*
staging.*
```

---

# 33. Relationship Summary

| Parent | Child | Relationship | Key |
|---|---|---|---|
| WorkerIdentity | NaukriProfile | 1 : 0..1 | WorkerID |
| WorkerIdentity | GigProfile | 1 : 0..1 | WorkerID |
| WorkerIdentity | CBNexusProfile | 1 : 0..1 | WorkerID |
| WorkerIdentity | SourceMapping | 1 : N | WorkerID |
| WorkerIdentity | AudioSubmission | 1 : N | WorkerID |

Central principle:

```text
                    WorkerID
                       |
       +---------------+---------------+
       |               |               |
     Naukri           Gig           CBNexus
```

---

# 34. Final Analytical Conclusions

Our analytics phase produced these major decisions:

- The three systems contain overlapping workers and inconsistent representations.
- `WorkerID` will be the internally generated global identity.
- `WorkerName` will be normalized to `Aa`/Title Case.
- Email will be lowercase and validated.
- Phone will use a canonical 10-digit representation.
- Location will be normalized and controlled.
- Skills will be consolidated and deduplicated.
- Recruitment information will be stored in `NaukriProfile`.
- Gig information will be stored in `GigProfile`.
- CBNexus information will be stored in `CBNexusProfile`.
- `WorkerID` will be the foreign-key relationship key.
- `WorkerName` will remain for readability but will not be used as a relationship key.
- Raw data will never be modified.
- Cleaning and normalization will occur in staging.
- Core tables will contain canonical validated data.
- Audit tables will preserve transformation and provenance information.
- The architecture can be extended to new sources and Task 3 audio submissions.

---

# 35. Current Project Status

```text
DATA ANALYSIS                       COMPLETE
DATA IRREGULARITY IDENTIFICATION   COMPLETE
CANONICAL RULES                    COMPLETE
ENTITY MODEL                       COMPLETE
RELATIONSHIPS                      COMPLETE
DATABASE MODEL                     COMPLETE
PIPELINE ARCHITECTURE              COMPLETE
SECURITY DESIGN                    COMPLETE
CHECKPOINT STRATEGY                COMPLETE

POSTGRESQL IMPLEMENTATION          NEXT
```

## Next Engineering Milestone

The next implementation sequence is:

```text
PostgreSQL Database
        ↓
Schemas
        ↓
Import Tracking
        ↓
Raw Tables
        ↓
Raw CSV Ingestion
        ↓
Structural Validation
        ↓
Normalization
        ↓
Semantic Validation
        ↓
Entity Resolution
        ↓
WorkerID Generation
        ↓
Core Tables
        ↓
Audit
        ↓
End-to-End Testing
        ↓
n8n Automation
        ↓
Task 3 Audio Application
```

---

# 36. Golden Rules

1. Never modify raw source data.
2. Never insert raw data directly into core tables.
3. Normalize before entity resolution.
4. WorkerID is the global relationship key.
5. WorkerName is readable data, not a foreign key.
6. Never merge workers using name alone.
7. Preserve source provenance.
8. Record every automatic correction.
9. Quarantine data that cannot be safely repaired.
10. Use database transactions for canonical writes.
11. Keep secrets out of Git.
12. Do not expose unnecessary PII in logs.
13. Make ingestion idempotent.
14. Test every layer independently before moving forward.
15. Design for future scale without sacrificing correctness.

