# MoMo SMS Analytics

This project processes MoMo (Mobile Money) SMS transaction data provided in XML
format. The pipeline parses, cleans, and categorizes the raw data, loads it into
a relational database, and exposes it through a frontend dashboard for analysis
and visualization.

The system is built as an ETL (Extract, Transform, Load) pipeline feeding a
lightweight dashboard, with a REST API layer for serving data dynamically.

---

## Team Members

- Albertine Umuhoza — Scrum board setup
- Eunice Nina Sangwa — Project structure & repository creation
- Karen Stephy Musangwa — README documentation
- Kevine Niyonkuru — Architecture diagram


- **Task sheet:** https://docs.google.com/spreadsheets/d/1RB45q7XWXbDKYkOpRhFR2NO7sjnrrtPxg9bo7fhqVe4/edit?gid=0#gid=0
- **Scrum board (Trello):** https://trello.com/b/rGnY8I6y/momo-sms-data-processing-analytics
- **Architecture diagram (Miro):** https://miro.com/app/board/uXjVHqF35hA=/?share_link_id=532822707039
- **Database design document:** https://drive.google.com/file/d/1Wmd7B-d48N7y6nHHCpJGrHxLH6LCPjdR/view?usp=sharing

---

## System Architecture

High-level flow:
XML input
│
▼
ETL pipeline (parse → clean → categorize → load)
│
▼
SQLite database
│
▼
JSON export
│
▼
Frontend dashboard

(+ REST API on top of the parsed data — see below)

text

---

## Project Structure
├── README.md # Setup, run, overview
├── .env.example # DATABASE_URL or path to SQLite
├── requirements.txt # No third-party deps for the REST API
├── index.html # Dashboard entry (static)
├── web/
│ ├── styles.css # Dashboard styling
│ ├── chart_handler.js # Fetch + render charts/tables
│ └── assets/ # Images/icons (optional)
├── data/
│ ├── raw/ # Provided XML input (git-ignored)
│ │ └── momo.xml
│ ├── processed/ # Cleaned/derived outputs for frontend
│ │ └── dashboard.json
│ ├── db.sqlite3 # SQLite DB file
│ ├── modified_sms_v2.xml # Source SMS dataset (1691 records)
│ └── logs/
│ ├── etl.log # Structured ETL logs
│ └── dead_letter/ # Unparsed/ignored XML snippets
├── etl/
│ ├── init.py
│ ├── config.py # File paths, thresholds, categories
│ ├── parse_xml.py # XML parsing (ElementTree)
│ ├── clean_normalize.py # Amounts, dates, phone normalization
│ ├── categorize.py # Simple rules for transaction types
│ ├── load_db.py # Create tables + upsert to SQLite
│ └── run.py # CLI: parse → clean → categorize → load → export JSON
├── api/
│ ├── init.py
│ ├── app.py # Plain http.server REST API (Basic Auth)
│ ├── auth.py # HTTP Basic Authentication
│ ├── storage.py # In-memory transaction store
│ ├── handlers_get.py # GET handlers
│ ├── handlers_write.py # POST / PUT / DELETE handlers
│ ├── schemas.py # Field definitions
│ └── db.py # SQLite connection helpers (placeholder)
├── scripts/
│ ├── run_etl.sh
│ ├── export_json.sh
│ ├── serve_frontend.sh
│ ├── linear_vs_dict.py # DSA benchmark (linear vs dict lookup)
│ └── test_api.sh # curl smoke tests
├── tests/
│ ├── test_parse_xml.py
│ ├── test_clean_normalize.py
│ ├── test_categorize.py
│ ├── test_auth.py
│ ├── test_handlers.py
│ └── test_dsa.py
├── docs/
│ ├── erd_diagram.png
│ ├── design_rationale.md
│ ├── api_docs.md
│ ├── report.md / report.pdf
│ └── architecture.png
├── database/
│ └── database_setup.sql
└── examples/
└── json_schemas.json

text

---

## Setup & Installation

Clone the repository:

```bash
git clone https://github.com/Eunice-Nina/momo-sms-analytics.git
cd momo-sms-analytics
Create a virtual environment (optional — the REST API uses only the Python
standard library):

bash
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy the environment file and configure it:

bash
cp .env.example .env
Running the Project
1. Run the ETL pipeline
bash
bash scripts/run_etl.sh
or directly:

powershell
python etl\run.py
Expected output:

text
Parsed 1691 records from ...\data\modified_sms_v2.xml
Wrote ...\data\transactions.json
2. Export the processed data for the dashboard
bash
bash scripts/export_json.sh
3. Serve the frontend dashboard
bash
bash scripts/serve_frontend.sh
Open index.html in your browser (or visit http://localhost:8000) to view
the dashboard.

REST API (Assignment: Building and Securing a REST API)
A plain-Python REST API (http.server) that serves the parsed SMS transactions
with HTTP Basic Authentication.

Run
powershell
python etl\run.py     # parse XML -> data/transactions.json
python api\app.py     # start server on http://localhost:8000
Default credentials: admin / secret123
Override with API_USER / API_PASS environment variables.

Endpoints
Method	Path	Description
GET	/transactions	List all transactions
GET	/transactions/{id}	Get one transaction
POST	/transactions	Create a transaction
PUT	/transactions/{id}	Update a transaction
DELETE	/transactions/{id}	Delete a transaction
Examples
powershell
curl -u admin:secret123 http://localhost:8000/transactions
curl -i -u admin:secret123 http://localhost:8000/transactions/1
curl -u admin:secret123 -X POST http://localhost:8000/transactions --json '{\"type\":\"TRANSFER\",\"amount\":1000}'
curl -u admin:secret123 -X PUT http://localhost:8000/transactions/1692 --json '{\"type\":\"TRANSFER\",\"amount\":2500}'
curl -u admin:secret123 -X DELETE http://localhost:8000/transactions/1692
curl -i -u admin:wrong http://localhost:8000/transactions
On Windows PowerShell, use curl.exe because curl is aliased to
Invoke-WebRequest. Or run Remove-Item alias:curl once per terminal.

Error codes
Code	Meaning
200	OK
201	Created
400	Bad Request (validation or invalid JSON)
401	Unauthorized (missing or invalid credentials)
404	Not Found
Full documentation: docs/api_docs.md.

Testing
Unit tests
powershell
python tests\test_parse_xml.py
python tests\test_auth.py
python tests\test_handlers.py
python tests\test_dsa.py
or with pytest:

bash
pytest tests/
DSA benchmark
powershell
python scripts\linear_vs_dict.py
Compares linear search O(n) with dictionary lookup O(1) average. Sample:

text
Records in test: 20
Target ID: 20
Linear search : 0.012385s for 10000 runs
Dict lookup   : 0.001094s for 10000 runs
Dictionary is 11.3x faster in this test
Screenshots
All API test evidence is in screenshots/.
See screenshots/README.md for the mapping between
each image and the rubric item.

Security Notes
The REST API uses HTTP Basic Authentication:

Client sends Authorization: Basic <base64(username:password)>.

Server decodes and compares against configured credentials.

Invalid credentials return 401 Unauthorized with
WWW-Authenticate: Basic realm="MoMo API".

Basic Auth is not secure for production:

Base64 is not encryption; credentials are readable if intercepted.

Credentials are sent on every request.

No expiry, revocation, or scopes.

Vulnerable to replay and MITM without HTTPS.

No rate limiting by default.

Recommended for production: JWT, OAuth2, HMAC-signed requests, or mutual
TLS — always over HTTPS.

Database Design (Week 2)
DDL: database/database_setup.sql

Design rationale: docs/design_rationale.md

ERD: docs/erd_diagram.png

Database design document: https://drive.google.com/file/d/1Wmd7B-d48N7y6nHHCpJGrHxLH6LCPjdR/view?usp=sharing

Core entities: Users, Transactions, Transaction_Categories,
System_Logs, plus a Transaction_Category_Map junction table that resolves
the many-to-many relationship between transactions and categories.

API/dashboard JSON shapes derived from this schema are documented in
examples/json_schemas.json.
```
---

Deliverables
Source code in this repository.

API documentation in docs/api_docs.md.

Screenshots in screenshots/.

**PDF report:** https://drive.google.com/file/d/1GkDFKQLkCAObEurNND0Wqo3TrWpWizmy/view?usp=sharing

**Team participation sheet:** https://docs.google.com/spreadsheets/d/1N8Cr2nGHCffUXWEApsXrDv_y98PNRbnut2XjAjWZfK4/edit?usp=sharing

**Scrum / Trello board:** https://trello.com/b/rGnY8I6y/momo-sms-data-processing-analytics

---
License
Academic project — not for redistribution.

