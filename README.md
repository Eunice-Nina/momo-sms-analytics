## Project Description

This project processes MoMo (Mobile Money) SMS transaction data provided in XML format. The pipeline parses, cleans, and categorizes the raw data, loads it into a relational database (SQLite), and exposes it through a frontend dashboard for analysis and visualization.

The system is built as an ETL (Extract, Transform, Load) pipeline feeding a lightweight dashboard, with an optional REST API layer for serving data dynamically.

## Team Members

- Albertine Umuhoza — Role : Scrum board setup
- Eunice Nina Sangwa — Role : Project structure & repository creation
- Karen Stephy Musangwa — Role : README documentation
- Kevine Niyonkuru — Role : Architecture diagram

## System Architecture

High-level design: XML input → ETL pipeline (parse → clean → categorize → load) → SQLite database → JSON export → frontend dashboard.

Architecture diagram: [Link to Draw.io / Miro diagram]

## Scrum Board

Tasks are tracked using [GitHub Projects / Trello / Jira].

Board link: https://trello.com/b/rGnY8I6y

## Project Structure

```
├── README.md                # Setup, run, overview
├── .env.example              # DATABASE_URL or path to SQLite
├── requirements.txt          # lxml/ElementTree, dateutil, (FastAPI optional)
├── index.html                # Dashboard entry (static)
├── web/
│   ├── styles.css             # Dashboard styling
│   ├── chart_handler.js       # Fetch + render charts/tables
│   └── assets/                # Images/icons (optional)
├── data/
│   ├── raw/                   # Provided XML input (git-ignored)
│   │   └── momo.xml
│   ├── processed/             # Cleaned/derived outputs for frontend
│   │   └── dashboard.json
│   ├── db.sqlite3             # SQLite DB file
│   └── logs/
│       ├── etl.log            # Structured ETL logs
│       └── dead_letter/       # Unparsed/ignored XML snippets
├── etl/
│   ├── __init__.py
│   ├── config.py               # File paths, thresholds, categories
│   ├── parse_xml.py            # XML parsing (ElementTree/lxml)
│   ├── clean_normalize.py      # Amounts, dates, phone normalization
│   ├── categorize.py           # Simple rules for transaction types
│   ├── load_db.py              # Create tables + upsert to SQLite
│   └── run.py                  # CLI: parse -> clean -> categorize -> load -> export JSON
├── api/                       # Optional (bonus)
│   ├── __init__.py
│   ├── app.py                  # Minimal FastAPI with /transactions, /analytics
│   ├── db.py                   # SQLite connection helpers
│   └── schemas.py               # Pydantic response models
├── scripts/
│   ├── run_etl.sh               # python etl/run.py --xml data/raw/momo.xml
│   ├── export_json.sh           # Rebuild data/processed/dashboard.json
│   └── serve_frontend.sh        # python -m http.server 8000 (or Flask static)
└── tests/
    ├── test_parse_xml.py
    ├── test_clean_normalize.py
    └── test_categorize.py
```

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone [repo-url]
   cd [repo-name]
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the environment file and configure it:
   ```bash
   cp .env.example .env
   ```

## Running the Project

1. Run the ETL pipeline to process the raw XML data:
   ```bash
   bash scripts/run_etl.sh
   ```

2. Export the processed data for the dashboard:
   ```bash
   bash scripts/export_json.sh
   ```

3. Serve the frontend dashboard:
   ```bash
   bash scripts/serve_frontend.sh
   ```

4. Open `index.html` in your browser (or visit `http://localhost:8000`) to view the dashboard.

## (Optional) Running the API

```bash
uvicorn api.app:app --reload
```

Available endpoints:
- `GET /transactions` — list of processed transactions
- `GET /analytics` — aggregated analytics data

## Testing

```bash
pytest tests/
```
