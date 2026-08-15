Yes. Replace your entire `README.md` with this **short, submission-ready version**:

````markdown
# ConsultBae Data Platform & Automation

Implementation of the ConsultBae AI Automation Take-Home Assignment.

## Assignment Status

| Task | Status |
|---|---|
| Task 1 — Merge / Core Database | ✅ Complete |
| Task 2 — n8n Automation | ✅ Complete |
| Task 3 — Audio Collection App | ✅ Complete |
| Task 4 — Data Issues Report | ✅ Complete |
| Task 5 — Stretch | ⏭️ Skipped |

## Tech Stack

- Python
- PostgreSQL
- n8n
- FastAPI
- React
- Vite
- Tailwind CSS
- FFmpeg
- pytest

## Project Structure

```text
├── automations/       # Automation definitions
├── audio_web/         # React audio collection app
├── data/raw/          # Source CSV files
├── docs/              # Documentation
├── n8n/               # n8n workflow exports
├── sql/schemas/       # PostgreSQL schemas
├── src/               # Data pipeline and API
├── tests/             # Tests
├── .env.example
├── requirements.txt
└── README.md
````

# Task 1 — Merge

The three source datasets (Naukri, Gig and CBNexus) are loaded into PostgreSQL.

Pipeline:

```text
CSV
 ↓
Validation
 ↓
Staging
 ↓
Normalization
 ↓
Identity Resolution
 ↓
Core PostgreSQL
```

Run:

```bash
python -m src.ingestion.load_to_staging
python -m src.database.load_core
python -m src.analytics.generate_baseline
```

Identity resolution uses normalized contact information and other attributes. Name alone is not treated as a definitive identity key.

# Task 2 — n8n Automation

The n8n workflow receives an applicant, checks PostgreSQL for an existing worker and produces either a duplicate or new-applicant result.

```text
Webhook
 ↓
PostgreSQL
 ↓
IF
 ├── Duplicate → Alert
 └── New       → NO_DUPLICATE
```

Workflow:

```text
n8n/task2_duplicate_alert.json
```

Example duplicate:

```text
Rahul Jain
rahul.jain34@example.in
9000000114
```

Result:

```text
DUPLICATE_DETECTED
W000012
```

# Task 3 — Audio Collection App

The application allows a worker to:

* Enter name and phone number
* Upload audio
* Submit audio
* Store the recording
* Extract audio metadata
* View previous submissions
* Play submitted recordings

Extracted metadata:

* Duration
* Sample rate
* Bitrate
* Loudness

## Start FastAPI

```bash
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

API:

```text
http://127.0.0.1:8000/docs
```

## Start React

```bash
cd audio_web
npm install
npm run dev
```

Application:

```text
http://localhost:5173
```

## Manual Test

Valid worker:

```text
Manish Reddy
9000000237
```

Test result:

```text
Audio submitted securely and processed!
```

Dashboard result:

```text
Duration:    1.00 s
Sample rate: 44100 Hz
Bitrate:     705 kbps
Loudness:    -9.2 dB
```

Invalid worker:

```text
9999999999
```

Result:

```text
No matching worker found in Core database.
```

No orphan upload was left by the rejected submission.

# Task 4 — Data Issues Report

The main issues found in the source datasets were:

* Inconsistent name capitalization and whitespace
* Different phone number formats
* Email case/whitespace differences
* Location variations
* Duplicate/inconsistent skills
* Mixed experience representations
* Mixed CTC representations and units
* Mixed date formats
* Inconsistent gig-rate formats
* Inconsistent Gig status capitalization
* Invalid Gig status value such as `Pune`
* Different CBNexus Boolean representations (`Y/N`, `Yes/No`, etc.)
* Repeated header value `Verified`
* Repeated header value `Projects Completed`
* Blank/missing values
* Structural/column-shift problems
* Duplicate people across source systems

Treatment included normalization, canonicalization, deterministic repair, deduplication and quarantine/flagging of ambiguous values.

The detailed report is available as:

```text
ConsultBae_Task4_Data_Issues_Report.pdf
```

# Stuck Log

## 1. n8n PostgreSQL parameter issue

The initial PostgreSQL lookup produced a `$1` parameter error.

I inspected the generated SQL and parameter mapping, then tested the database query independently. I corrected the n8n query/parameter configuration instead of replacing the database lookup with custom code because the assignment specifically required a no-code/low-code automation.

## 2. n8n webhook test mode

The test webhook initially returned:

```text
The requested webhook is not registered.
```

I checked the n8n error message and learned that the test webhook must be registered by executing the workflow. I then executed the workflow and tested it using PowerShell `Invoke-RestMethod`.

I kept the test and production webhook URLs separate rather than treating the test URL as the permanent endpoint.

## 3. Tailwind CSS

The React application initially loaded without the intended Tailwind styling.

I inspected `package.json`, Vite configuration, Tailwind configuration and installed dependencies. I fixed the Tailwind/PostCSS setup and added the required PostCSS configuration.

I rejected replacing Tailwind with handwritten CSS because the existing application was already structured around Tailwind and the issue was configuration-related.

# Data Quality Principles

* Preserve raw source data
* Normalize before identity matching
* Never match people by name alone
* Normalize phone and email before matching
* Do not silently guess ambiguous values
* Flag or quarantine unresolved issues
* Preserve source lineage
* Keep normalization deterministic
