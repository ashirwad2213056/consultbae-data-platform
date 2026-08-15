# ConsultBae Data Platform
# Global Data Standard & Database Consistency Rules

**Document:** Global Data Rules v1.0  
**Purpose:** Canonical standard for data cleaning, validation, normalization, entity resolution, database storage, and future source integration.  
**Database:** PostgreSQL  
**Status:** Baseline specification — must be versioned when rules change.

---

# 1. Purpose

This document defines the **single global set of data rules** that every current and future ingestion pipeline must follow.

The objective is to ensure that:

- the same data is represented consistently;
- all three existing CSV sources follow one canonical standard;
- future source systems can be added without changing the identity model;
- cleaning decisions are deterministic and reproducible;
- raw source information is never lost;
- invalid data is not silently inserted into the core database;
- entity resolution remains safe;
- database constraints enforce the canonical model.

The rule is:

> **Source systems may differ. The canonical database representation must not.**

---

# 2. Rule Hierarchy

Rules must be applied in this order:

```text
SOURCE DATA
    |
    v
1. RAW PRESERVATION
    |
    v
2. STRUCTURAL VALIDATION
    |
    v
3. FIELD NORMALIZATION
    |
    v
4. SEMANTIC VALIDATION
    |
    v
5. ENTITY RESOLUTION
    |
    v
6. CANONICAL TRANSFORMATION
    |
    v
7. DATABASE CONSTRAINTS
    |
    v
8. AUDIT
```

Never reverse this order unless an explicitly documented exception exists.

---

# 3. Global Principles

## Rule G-01 — Raw data is immutable

Original source data must never be overwritten.

```text
CSV
 ↓
RAW
 ↓
STAGING
 ↓
CORE
```

Never:

```text
CSV
 ↓
modify CSV
 ↓
CORE
```

---

## Rule G-02 — Canonical values are standardized

Different source representations of the same logical value must map to one canonical representation.

Example:

```text
PUNE
pune
Pune
```

must become:

```text
Pune
```

---

## Rule G-03 — Normalization must be deterministic

For the same valid input:

```text
same input
    ↓
same rule
    ↓
same output
```

No random or non-reproducible transformations are permitted.

---

## Rule G-04 — Never silently discard data

Every discarded/rejected/quarantined record must have a reason recorded.

---

## Rule G-05 — Preserve provenance

Every processed record must remain traceable to:

```text
source system
batch
source row/record
processing result
```

---

## Rule G-06 — Core database contains canonical data

The `core` schema must contain only data that has passed the required validation rules.

---

## Rule G-07 — WorkerID is the global identity

`WorkerID` is the canonical global identifier across all source systems.

It must be:

- unique;
- stable;
- immutable;
- generated internally;
- independent of source-specific IDs.

---

# 4. Global Worker Identity Rules

## 4.1 WorkerID

### Canonical format

Recommended:

```text
W000001
W000002
W000003
```

### Requirements

- Primary key.
- Unique.
- Not reused.
- Must not change because a person's name, email, phone or location changes.
- Must not depend on source-system identifiers.

### Prohibited

Do not use:

```text
WorkerName
Email
Phone
SourceRecordID
```

as the global primary key.

---

# 5. Worker Name Rules

## Canonical format

Use:

```text
Aa / Title Case
```

Examples:

```text
RAHUL CHOPRA -> Rahul Chopra
rahul chopra -> Rahul Chopra
RAHUL    CHOPRA -> Rahul Chopra
```

## Processing rules

1. Remove leading whitespace.
2. Remove trailing whitespace.
3. Collapse repeated internal spaces.
4. Normalize capitalization.
5. Preserve meaningful punctuation where possible.
6. Do not remove legitimate name components.
7. Do not use the name as a unique identifier.

## Important

Name normalization is for consistency.

It does **not** prove identity.

---

# 6. Email Rules

## Canonical format

```text
lowercase
```

with leading/trailing whitespace removed.

Example:

```text
ISHA.CHOPRA95@EXAMPLE.ORG
        ↓
isha.chopra95@example.org
```

## Processing

```text
trim
 ↓
lowercase
 ↓
basic syntax validation
```

## Rules

- Store normalized email in the canonical database.
- Preserve original email in raw/audit data.
- Do not reject solely because the domain appears synthetic/test-like.
- Invalid syntax must be flagged.
- Do not automatically create a new WorkerID simply because email is missing.

---

# 7. Phone Rules

## Canonical representation

For the current India-focused dataset:

```text
10 digits
```

Example:

```text
9000000295
```

## Accepted source representations

The normalization layer may encounter:

```text
+91-9000000295
+91 9000000295
919000000295
09000000295
9000000295
```

where a reliable transformation exists.

## Canonical transformation

```text
+91-9000000295
        ↓
9000000295
```

## Rules

1. Remove formatting characters where safe.
2. Normalize country/prefix representation.
3. Validate the resulting number.
4. Canonical value must contain exactly 10 digits.
5. Do not invent missing digits.
6. Do not guess a phone number.
7. Invalid values must be flagged/quarantined.

---

# 8. Location Rules

## Canonical representation

Use standardized human-readable city/location names.

Examples:

```text
PUNE -> Pune
pune -> Pune
```

Controlled aliases may be defined:

```text
Bangalore -> Bengaluru
Gurgaon -> Gurugram
```

## Rules

- Trim whitespace.
- Collapse repeated whitespace.
- Normalize capitalization.
- Apply only approved aliases.
- Do not automatically merge geographically related terms without an explicit mapping rule.

Example:

```text
Delhi
New Delhi
Delhi NCR
```

must not automatically be treated as identical unless the mapping table explicitly says so.

---

# 9. Skills Rules

## Canonical representation

Skills must be:

- trimmed;
- normalized;
- deduplicated;
- consistently capitalized.

Example:

```text
" python, React, python, MongoDB "
```

becomes:

```text
Python, React, MongoDB
```

## Rules

1. Split skills according to the source delimiter.
2. Trim each skill.
3. Normalize capitalization.
4. Remove exact duplicates.
5. Preserve meaningful multi-word skills.
6. Do not merge semantically different skills without an approved mapping.

Example:

```text
React
ReactJS
React.js
```

must not automatically become one value unless the canonical skill dictionary explicitly defines the equivalence.

---

# 10. Work Experience Rules

## Canonical type

```text
NUMERIC / DECIMAL
```

## Canonical unit

```text
years
```

Examples:

```text
4.2
3.5
7.0
```

Do not store:

```text
"4.2 years"
```

in the canonical numeric field.

## Validation

```text
experience >= 0
```

Unreasonable or ambiguous values should be flagged rather than guessed.

---

# 11. CTC Rules

## Canonical unit

```text
INR
```

## Canonical field

```text
current_ctc_inr
```

## Important interpretation rule

Source values may represent different units.

For example:

```text
4.2
```

may represent:

```text
4.2 LPA
```

and therefore:

```text
420000 INR
```

The conversion must only happen according to a documented source-specific interpretation rule.

## Rules

1. Preserve original source value.
2. Identify source/unit interpretation.
3. Convert to canonical INR.
4. Store only canonical numeric value in the core field.
5. Do not guess ambiguous CTC units.
6. Flag ambiguous values.

---

# 12. Date Rules

## Canonical database type

```text
DATE
```

## Canonical representation

```text
YYYY-MM-DD
```

## Accepted source formats

May include:

```text
DD-MM-YYYY
YYYY-MM-DD
MM/DD/YYYY
DD Mon YYYY
```

## Rules

1. Parsing must be source-aware.
2. Ambiguous dates must not be guessed.
3. Invalid calendar dates must be rejected/quarantined.
4. Original source representation must remain available in raw/audit data.
5. Canonical database stores a proper PostgreSQL `DATE`.

---

# 13. Gig Rate Rules

Do not store rate and unit together in the canonical database.

Use:

```text
rate_amount
rate_unit
```

Examples:

```text
1415/hr
```

becomes:

```text
rate_amount = 1415
rate_unit = HOUR
```

```text
15k/month
```

becomes:

```text
rate_amount = 15000
rate_unit = MONTH
```

## Canonical rate units

Initial allowed values:

```text
HOUR
DAY
WEEK
MONTH
PROJECT
```

The list must be controlled.

Unknown units must be flagged rather than silently converted.

---

# 14. Status Rules

## Canonical values

```text
ACTIVE
INACTIVE
PAUSED
```

## Processing

Case differences are normalized:

```text
active
Active
ACTIVE
```

all become:

```text
ACTIVE
```

## Rules

- Trim.
- Normalize case.
- Validate against allowed values.
- Unknown values are invalid.
- Do not convert an unrelated value into a status merely because it is present in the status column.

---

# 15. Verified Rules

## Canonical database type

```text
BOOLEAN
```

## Mapping

```text
Y
Yes
yes
YES
```

become:

```text
TRUE
```

and:

```text
N
No
no
NO
```

become:

```text
FALSE
```

## Rules

- Trim.
- Normalize case.
- Apply explicit mapping.
- Unknown values are flagged.
- Do not guess.

---

# 16. Projects Completed Rules

## Canonical type

```text
INTEGER
```

## Validation

```text
projects_completed >= 0
```

Rules:

- Must represent a whole number.
- Negative values are invalid.
- Non-numeric values are invalid unless an explicit deterministic conversion exists.

---

# 17. Missing Value Rules

Missing values must be represented consistently.

## Canonical database representation

Use:

```text
NULL
```

rather than arbitrary strings such as:

```text
N/A
NA
unknown
-
none
not available
```

unless the field specifically requires such a value.

## Rule

Do not convert a meaningful unknown state into an invented value.

---

# 18. Empty String Rules

For fields where an empty value has no semantic meaning:

```text
""
"   "
```

should normally become:

```text
NULL
```

after trimming.

Exception: fields where empty string has an explicitly defined business meaning.

---

# 19. Structural Validation Rules

Before field normalization, every source file must be checked for:

```text
Expected headers
Unexpected headers
Column count
Repeated headers
Blank rows
Malformed rows
Column shifts
Unexpected columns
Missing columns
Encoding problems
Delimiter problems
```

## Repeated headers

A repeated header inside a dataset must not become a worker record.

Example:

```text
Name | Phone | City | Verified
```

appearing after data rows should be recognized as a header and excluded from canonical processing.

The raw row remains preserved.

---

# 20. Column Shift Rules

If a value appears under the wrong field:

```text
Location <- status
```

the pipeline must not silently assign a new meaning.

Processing:

```text
Detect
 ↓
Attempt deterministic repair only if rule exists
 ↓
Audit repair
 ↓
Otherwise quarantine
```

Never guess.

---

# 21. Data Quality Classification

Every problematic value/record must receive one of:

```text
VALID
WARNING
REPAIRABLE
REJECTED
FATAL
```

## VALID

No issue.

## WARNING

Safe normalization occurred.

Example:

```text
PUNE -> Pune
```

## REPAIRABLE

A deterministic corruption was safely repaired.

Example:

```text
Repeated header -> excluded
```

## REJECTED

The record cannot be safely interpreted.

## FATAL

A system-level error prevents safe processing.

---

# 22. Entity Resolution Rules

Entity resolution must happen **after normalization**.

Order:

```text
Raw
 ↓
Normalize
 ↓
Validate
 ↓
Match
```

Never perform identity matching primarily on raw unnormalized values.

---

# 23. Identity Matching Hierarchy

Use this order:

```text
1. Exact normalized email
        ↓
2. Exact normalized phone
        ↓
3. Strong combinations
        ↓
4. Fuzzy candidate matching
        ↓
5. Manual review / quarantine
```

Strong combinations:

```text
Name + Phone
Name + Email
Name + Phone + Location
```

---

# 24. Name-Only Matching Rule

Never automatically merge workers based only on name.

Incorrect:

```text
Deepak Nair
       =
Deepak Nair
```

A name is an attribute, not sufficient proof of identity.

---

# 25. Fuzzy Matching Rule

Fuzzy matching must be treated as a candidate-generation mechanism, not automatic proof of identity.

Use confidence:

```text
HIGH
MEDIUM
LOW
UNMATCHED
```

Low-confidence candidates must not be silently merged.

---

# 26. WorkerID Assignment Rules

When an existing worker is confidently identified:

```text
reuse existing WorkerID
```

When a genuinely new worker is identified:

```text
generate new WorkerID
```

Never:

```text
generate new WorkerID
```

merely because formatting differs.

---

# 27. WorkerID Immutability

Once assigned:

```text
W000001
```

must remain:

```text
W000001
```

even if:

```text
Name changes
Email changes
Phone changes
Location changes
```

Identity history must not be lost.

---

# 28. Source Precedence Rules

When multiple sources provide different values for the same worker, the pipeline must not blindly overwrite one source with another.

A future source-precedence policy should be explicitly documented per field.

For example:

```text
Identity fields:
Email / Phone / Location
```

may require conflict handling.

Profile-specific fields should generally remain associated with their source profile.

When sources conflict:

```text
Do not silently overwrite.
Record conflict.
Apply documented precedence if one exists.
Otherwise retain source-specific values and flag the conflict.
```

---

# 29. WorkerName in Profile Tables

`WorkerName` may be retained in:

```text
WorkerIdentity
NaukriProfile
GigProfile
CBNexusProfile
```

for readability.

However:

```text
WorkerID = relationship key
WorkerName = readable attribute
```

WorkerName must never be the foreign key.

---

# 30. Skills Consolidation Rule

If the same worker has skills in multiple trusted sources:

```text
Source A:
Python, React

Source B:
Python, MongoDB
```

the canonical Worker Identity skill set may become:

```text
Python, React, MongoDB
```

provided the records have been confidently resolved to the same worker.

Do not combine skills from unresolved workers.

---

# 31. Source-Specific Data Rule

Source-specific attributes must remain in their relevant profile.

### Naukri

```text
WorkExperience
CTC
AppliedDate
```

### Gig

```text
Rate
RateUnit
Status
```

### CBNexus

```text
Verified
ProjectsCompleted
```

Do not move source-specific fields into Worker Identity merely for convenience.

---

# 32. Database Layer Rules

Use:

```text
raw
staging
core
audit
```

## RAW

Permissive.

Purpose:

```text
source preservation
```

## STAGING

Normalized and validated.

Purpose:

```text
data preparation
```

## CORE

Canonical and constrained.

Purpose:

```text
business database
```

## AUDIT

Traceability.

Purpose:

```text
lineage
quality
errors
transformations
```

---

# 33. Core Database Rules

Core tables must use:

- primary keys;
- foreign keys;
- appropriate PostgreSQL data types;
- NOT NULL where justified;
- CHECK constraints;
- indexes;
- controlled values.

Core should reject data that violates canonical rules.

---

# 34. Primary Key Rules

`WorkerID`:

```text
PRIMARY KEY
```

Profile tables:

```text
WorkerID PRIMARY KEY
WorkerID FOREIGN KEY -> WorkerIdentity.WorkerID
```

This creates one-to-zero-or-one relationships for the three source profiles.

---

# 35. Foreign Key Rules

Every profile `WorkerID` must exist in:

```text
core.worker_identity
```

No orphan profile is allowed.

Conceptually:

```text
WorkerIdentity
      |
      +---- NaukriProfile
      |
      +---- GigProfile
      |
      +---- CBNexusProfile
```

---

# 36. Uniqueness Rules

Global WorkerID must always be unique.

Do not automatically make every attribute unique.

For example, email/phone uniqueness should only be enforced after considering the real business semantics and source behavior.

Potential shared contact information must not accidentally create identity corruption.

---

# 37. Audit Rules

Every important transformation should record:

```text
source
batch
row
field
original value
normalized value
rule
action
severity
timestamp
```

Example:

```text
Source: GIG
Row: 15
Field: Status

Original:
"active"

Normalized:
"ACTIVE"

Rule:
STATUS_CASE_NORMALIZATION

Action:
TRANSFORMED
```

---

# 38. Provenance Rules

Every canonical worker should be traceable to source records.

Recommended technical mapping:

```text
WorkerID
SourceSystem
SourceRecordID
SourceRowNumber
```

Example:

```text
W000001 -> NAUKRI -> row 7
W000001 -> GIG -> row 12
W000001 -> CBNEXUS -> row 18
```

---

# 39. Batch Rules

Every ingestion must create a batch record.

Batch should contain:

```text
batch_id
source_system
file_name
file_hash
started_at
completed_at
status
row counts
```

Possible batch statuses:

```text
PROCESSING
COMPLETED
FAILED
PARTIAL
QUARANTINED
```

---

# 40. File Hash Rules

Calculate SHA-256 for every incoming file.

Purpose:

- identify exact duplicate files;
- support idempotency;
- establish file lineage;
- distinguish file versions.

Conceptually:

```text
file
 ↓
SHA-256
 ↓
file_hash
 ↓
import_batch
```

---

# 41. Idempotency Rules

Processing the exact same source file twice must not create duplicate workers.

Use:

```text
file_hash
batch tracking
source record identity
WorkerID resolution
database constraints
```

Expected:

```text
Run 1 Worker Count
       =
Run 2 Worker Count
```

for an unchanged source file.

---

# 42. Transaction Rules

Canonical writes must use transactions where atomicity is required.

Example:

```text
BEGIN
   |
   +-- Worker
   |
   +-- Profile
   |
COMMIT
```

If a critical write fails:

```text
ROLLBACK
```

No partial canonical record should remain.

---

# 43. Security Rules

## Secrets

Never commit:

```text
.env
database passwords
API keys
tokens
n8n credentials
```

## Database User

Application should use a restricted PostgreSQL user.

Do not use the PostgreSQL superuser for normal application operations.

## Logs

Do not log unnecessary PII.

Use masking where possible:

```text
Phone: ******0295
Email: is***@example.org
```

## Raw Data

Raw data should have controlled access.

---

# 44. Quarantine Rules

Records that cannot be safely repaired must go to quarantine.

Examples:

```text
Invalid phone
Ambiguous date
Unknown status
Unresolvable column shift
Low-confidence identity match
```

Quarantine record should contain:

```text
source
batch
row
original data/reference
reason
error type
timestamp
```

Never delete problematic source data simply because it is invalid.

---

# 45. Error Handling Rules

## Field-level problem

Try deterministic normalization.

## Record-level problem

Quarantine if safe interpretation is impossible.

## Batch-level problem

Mark batch as failed.

## System-level problem

Stop processing safely and preserve raw data.

---

# 46. Future Source Integration Rules

Any future source must go through:

```text
Source Adapter
     ↓
Raw
     ↓
Structural Validation
     ↓
Canonical Normalization
     ↓
Semantic Validation
     ↓
Entity Resolution
     ↓
Existing WorkerID / New WorkerID
     ↓
Core
```

A new source must not create a separate worker identity model.

---

# 47. Schema Evolution Rules

When adding a new field:

1. Define business meaning.
2. Define canonical data type.
3. Define normalization rule.
4. Define validation rule.
5. Define nullability.
6. Define source mapping.
7. Define audit behavior.
8. Add migration.
9. Add tests.
10. Update this document's version.

Do not modify the production schema manually without recording the change.

---

# 48. Rule Change Management

This document is a versioned specification.

When a canonical rule changes:

```text
v1.0
 ↓
document change
 ↓
migration/test
 ↓
v1.1
```

Never silently change a rule in code without updating the specification.

---

# 49. Backward Compatibility

A rule change must consider existing records.

Example:

If a location mapping changes:

```text
Old:
Bangalore

New:
Bengaluru
```

we must decide whether existing data is migrated.

The decision must be documented.

---

# 50. Testing Rules

Every normalization function must have tests for:

### Normal

```text
Rahul Chopra
```

### Uppercase

```text
RAHUL CHOPRA
```

### Lowercase

```text
rahul chopra
```

### Whitespace

```text
  Rahul   Chopra
```

### Alternate format

```text
+91-9000000295
```

### Invalid value

```text
invalid
```

---

# 51. Entity Resolution Testing

Minimum cases:

```text
Same person / same email
Same person / different email case
Same person / different phone formatting
Same person / name variation
Same name / different people
Missing email
Missing phone
Conflicting attributes
Low-confidence candidate
```

No automatic merge should occur where confidence is insufficient.

---

# 52. Data Quality Metrics

Every pipeline run should calculate:

```text
total_rows
valid_rows
normalized_rows
warning_rows
repaired_rows
rejected_rows
quarantined_rows
unique_workers
duplicate_candidates
matched_workers
new_workers
```

These metrics should be available for reporting.

---

# 53. Data Quality KPIs

Useful KPIs:

## Validity Rate

```text
valid rows / total rows
```

## Normalization Rate

```text
normalized rows / total rows
```

## Rejection Rate

```text
rejected rows / total rows
```

## Match Rate

```text
matched source records / total source records
```

## Duplicate Prevention

```text
duplicate workers created = 0
```

---

# 54. Future Audio Data Rules

Task 3 can extend the Worker model.

Proposed:

```text
AudioSubmission
-------------------------
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

The same `WorkerID` must be used.

A new audio submission must not create a new worker identity.

---

# 55. Scalability Rules

The system should remain correct before being optimized for extreme scale.

When scale increases:

1. Batch processing.
2. Database indexes.
3. Connection pooling.
4. Efficient bulk inserts.
5. Pagination/chunking.
6. Queue-based processing if necessary.
7. Idempotent jobs.
8. Retry-safe transactions.
9. Monitoring.
10. Horizontal scaling of stateless processing components where appropriate.

Do not prematurely introduce complexity that is not needed.

---

# 56. Golden Rules

These rules override convenience:

1. **Never modify raw source data.**
2. **Never silently discard data.**
3. **Never invent missing values.**
4. **Never merge workers using name alone.**
5. **Normalize before entity resolution.**
6. **WorkerID is the global identity.**
7. **WorkerID is immutable.**
8. **WorkerName is not an identity key.**
9. **Source-specific attributes stay in source-specific profiles.**
10. **Core data must be canonical and validated.**
11. **Every transformation must be auditable.**
12. **Every batch must be traceable.**
13. **Every exact file should be safely reprocessable without duplicates.**
14. **Unknown values must be flagged, not guessed.**
15. **Database constraints must protect the canonical model.**
16. **Secrets must never enter source control.**
17. **PII must not be unnecessarily exposed in logs.**
18. **Low-confidence entity matches must not be silently merged.**
19. **New sources must use the existing global identity model.**
20. **Any rule change must update this specification and its tests.**

---

# 57. Canonical Field Reference

| Entity | Field | Canonical Type | Canonical Rule |
|---|---|---|---|
| Worker | WorkerID | VARCHAR | Global immutable ID |
| Worker | WorkerName | VARCHAR | Title Case |
| Worker | Email | VARCHAR | Lowercase + trim |
| Worker | Phone | VARCHAR(10) | 10 digits |
| Worker | Location | VARCHAR | Controlled canonical name |
| Worker | Skills | TEXT | Normalized + deduplicated |
| Naukri | WorkExperience | NUMERIC | Years |
| Naukri | CTC | NUMERIC | INR |
| Naukri | AppliedDate | DATE | PostgreSQL DATE |
| Gig | RateAmount | NUMERIC | Numeric amount |
| Gig | RateUnit | ENUM/VARCHAR | Controlled unit |
| Gig | Status | ENUM/VARCHAR | ACTIVE/INACTIVE/PAUSED |
| CBNexus | Verified | BOOLEAN | TRUE/FALSE |
| CBNexus | ProjectsCompleted | INTEGER | >= 0 |

---

# 58. Canonical Database Model

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

Supporting technical schemas:

```text
raw.*
staging.*
audit.*
```

---

# 59. Rule Application Example

Suppose a future source sends:

```text
Name:
  RAHUL   CHOPRA

Email:
RAHUL.CHOPRA@EXAMPLE.COM

Phone:
+91-9000000295

City:
PUNE

Verified:
yes
```

The pipeline must produce:

```text
WorkerName:
Rahul Chopra

Email:
rahul.chopra@example.com

Phone:
9000000295

Location:
Pune

Verified:
TRUE
```

Then entity resolution determines:

```text
Existing WorkerID:
W000001
```

The core database receives only the canonical representation.

The raw layer retains the original values.

The audit layer records the transformations.

---

# 60. Final Governance Statement

This document is the **global canonical data contract** for the ConsultBae system.

All current and future data sources must conform to it before entering the `core` database.

The architecture deliberately separates:

```text
SOURCE REPRESENTATION
        ↓
CANONICAL REPRESENTATION
```

The source is allowed to be messy.

The core database is not.

When a new source, field, rule, or transformation is introduced, the change must be evaluated against:

```text
Identity
Consistency
Validity
Traceability
Security
Backward compatibility
Scalability
```

Only after the rule is defined and tested should it be implemented in the pipeline.

---

# 61. Document Version

```text
Document: Global Data Standard & Database Consistency Rules
Version: 1.0
Database: PostgreSQL
Status: Baseline
```

Future changes should increment the version and document:

```text
Change
Reason
Affected fields
Migration required?
Backward compatibility
Tests added
Date
```

