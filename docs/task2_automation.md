Sure. For `docs/task2\_automation.md`, paste this \*\*single-page version\*\* into Notepad:



````markdown

\# Task 2 — n8n Duplicate Alert Automation



\## Objective



Build one working no-code/low-code automation using n8n that receives a new applicant, checks the applicant against the PostgreSQL database, and sends a duplicate alert when an existing worker is found.



\## Technology



\- Automation: n8n

\- Database: PostgreSQL

\- Database: `consultbae\_db`

\- Core table: `core.workers`

\- Alert: HTTP POST webhook

\- Workflow artifact: `n8n/task2\_duplicate\_alert.json`



\## Workflow



```text

Applicant JSON

&#x20;    ↓

Webhook

&#x20;    ↓

PostgreSQL

&#x20;    ↓

IF: worker\_id is not empty

&#x20;  ┌───────────────┴───────────────┐

&#x20;  ↓                               ↓

TRUE                            FALSE

&#x20;  ↓                               ↓

HTTP Request                  Edit Fields

&#x20;  ↓                               ↓

Duplicate Alert               NO\_DUPLICATE

````



\## Input



The webhook accepts:



```json

{

&#x20; "name": "Rahul Jain",

&#x20; "email": "rahul.jain34@example.in",

&#x20; "phone": "9000000114"

}

```



\## Database Check



The PostgreSQL node searches `core.workers` using the applicant's email or phone and returns:



\* `worker\_id`

\* `canonical\_name`

\* `email`

\* `phone\_10`



The IF node checks:



```text

{{ $json.worker\_id }}

```



Condition:



```text

is not empty

```



`Always Output Data` is enabled on the PostgreSQL node so that a query returning no rows can continue to the FALSE branch.



\## Duplicate Alert



When an existing worker is found, the HTTP Request node sends:



```json

{

&#x20; "event": "DUPLICATE\_DETECTED",

&#x20; "worker\_id": "W000012",

&#x20; "name": "Rahul Jain",

&#x20; "email": "rahul.jain34@example.in",

&#x20; "phone": "9000000114"

}

```



The alert was successfully received by the configured webhook endpoint.



\## No-Duplicate Handling



When no worker exists, the FALSE branch produces:



```json

{

&#x20; "event": "NO\_DUPLICATE",

&#x20; "message": "Applicant does not exist in Core database",

&#x20; "name": "Test Applicant Unique",

&#x20; "email": "unique.test.2026@example.com",

&#x20; "phone": "8999999999"

}

```



No duplicate alert is generated.



\## Production Webhook



```text

http://localhost:5678/webhook/consultbae/new-applicant

```



The workflow was published and successfully tested using the production webhook.



\## Test Results



\### Existing Applicant — PASS



```text

Rahul Jain

rahul.jain34@example.in

9000000114

```



Database match:



```text

W000012

```



Result:



```text

DUPLICATE\_DETECTED

```



\### New Applicant — PASS



```text

Test Applicant Unique

unique.test.2026@example.com

8999999999

```



Database match:



```text

None

```



Result:



```text

NO\_DUPLICATE

```



\## Security



The exported workflow contains a PostgreSQL credential reference but does not contain the database password or other application secrets. Credentials remain managed separately by n8n/environment configuration.



\## Artifact



The complete exported n8n workflow is stored at:



```text

n8n/task2\_duplicate\_alert.json

```



\## Result



Task 2 is implemented and verified end-to-end. The automation receives applicant data, checks the PostgreSQL core database, detects duplicates, sends an alert for existing workers, and safely handles new applicants without generating a duplicate alert.



````



