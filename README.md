# ConsultBae Data Platform & Automation

This repository houses the end-to-end data platform, automation, and applications for the ConsultBae AI Automation Assignment.

## Current Project Status

### ✅ Task 1: Merged Core Database (`PostgreSQL`)
- **Ingestion**: Raw data from Naukri, Gig, and CBNexus is successfully parsed and loaded to staging.
- **Normalization & Validation**: Robust rules are applied to fix malformed files (e.g. Gig column shifts), validate schemas, and normalize statuses, contact information, and skills.
- **Identity Resolution**: Matching algorithms unify records corresponding to the same person without relying on strict ID consistency. 
- **Core Database**: Consolidated records (Worker Identity, Worker Skills, and 3x Source profiles) are successfully loaded uniquely into a standardized `core` PostgreSQL schema. 

### ✅ Task 2: No-Code Automation (`n8n`)
- Configured a native n8n webhook workflow to intercept incoming applicant records.
- Queries the backend PostgreSQL `core.workers` table using safe parameterized inputs.
- Detects identity collisions based on `email` or `phone_10` and fires a Slack/Discord webhook alert.
- **Location**: Definition exported to `automations/task2_duplicate_alert.json`. 

### ⏳ Task 3: Audio Collection Web App
- *Pending Implementation*

### ⏳ Task 4: Data Issues Report
- *In progress*. A comprehensive list of data constraints, anomalies, and structural defects discovered and resolved during Task 1.

---

## Directory Architecture

```text
├── automations/            # n8n workflows and architecture docs
├── data/                    
│   └── raw/                # Source CSV files
├── docs/                   # Project documentation and specifications
│
├── src/                    # Data Pipeline Toolkit
│   ├── config/             # Environment and settings
│   ├── ingestion/          # Pipeline runners, identity resolution
│   ├── validation/         # Data schema and structural checks
│   ├── normalization/      # Value standardization rules
│   ├── database/           # Postgres drivers and core loading
│   └── analytics/          # Business intelligence scripts
│
├── sql/                    # Raw schema definitions
│   └── schemas/            
│
├── tests/                  # Pytest unit & integration test suites
│
├── .env.example
├── requirements.txt
└── README.md
```

## Setup & Execution

### 1. Requirements
Ensure Python 3.10+, PostgreSQL, and Git are installed. For Task 2, `npx n8n` is recommended.

### 2. Environment
Create a `.env` file copying the `.env.example` file and specifying your PostgreSQL database credentials:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Running Data Pipeline (Task 1)
```bash
python -m src.ingestion.load_to_staging
python -m src.database.load_core
# To view Analytics:
python -m src.analytics.generate_baseline
```

### 4. Running Automation (Task 2)
```bash
npx n8n
# Navigate to http://localhost:5678, configure Postgres credentials, and import automations/task2_duplicate_alert.json
```
