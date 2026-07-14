# WealthCraft — Professional Financial Planning System

Enterprise-grade financial planning platform for wealth advisors. Generate fully automated, consulting-quality financial plans for **any client** using configurable forms — **no hardcoded personal data**.

Inspired by workflows used at leading Indian wealth firms (DSP, ICICI Prudential, Motilal Oswal, Edelweiss, HDFC Securities), with modular architecture and production-ready reporting.

---

## Features

- **Multi-client CRM** with JWT authentication
- **Configurable inputs**: personal, income, expenses, loans, assets, insurance, investments, goals, tax, risk, assumptions
- **Financial engine** (pure Python / NumPy / Pandas / SciPy):
  - Net worth, cash flow, savings & DTI ratios
  - Emergency fund, goal SIP/lumpsum, retirement corpus
  - EMI amortization & prepayment analysis
  - Old vs New Indian tax regime comparison (FY 2025-26)
  - HLV / insurance need analysis
  - Portfolio allocation & JSON-driven recommendations (no hardcoded schemes)
  - Monte Carlo retirement simulation, FIRE number, health score
  - Scenario & what-if analysis
- **One-click generation**: Dashboard + Excel + PDF + Charts + Recommendations
- **Excel workbook**: 30+ professionally formatted sheets
- **PDF plan**: multi-section 30–50 page advisory report
- **Dark / light UI** with Recharts dashboards

---

## Architecture

```
frontend/           React + TypeScript + Tailwind + shadcn-style UI
backend/            FastAPI + JWT auth + REST API
financial_engine/   Pure Python calculation engine
excel_generator/    openpyxl multi-sheet workbook
pdf_generator/      ReportLab multi-page plan
charts/             Matplotlib chart PNGs
database/           SQLAlchemy models (SQLite / PostgreSQL)
config/             Assumptions, recommendations, risk questionnaire (JSON)
sample_data/        Demo client profile (illustrative only)
tests/              Unit & integration tests
deploy/             Nginx config for Docker
```

---

## Quick Start (Development)

### Prerequisites

- **Python 3.11 or 3.12** (recommended — avoid 3.14 for now; several scientific packages may lack wheels)
- Node.js 20+
- npm

### Backend

```bash
# Prefer Python 3.12 if multiple versions are installed:
#   python3.12 -m venv .venv
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env

export PYTHONPATH=.
uvicorn backend.main:app --reload --port 8000
```

Local development uses **SQLite** — no PostgreSQL install required.

PostgreSQL (optional / production):

```bash
pip install -r requirements-postgres.txt
# DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/financial_planner
```

#### Install troubleshooting

| Error | Fix |
|-------|-----|
| `pg_config executable not found` / `psycopg2-binary` build fails | You don’t need it for local SQLite. Pull latest `requirements.txt` (Postgres is optional) or use Python 3.12. |
| `uvicorn: command not found` | Install failed earlier — recreate the venv, then `pip install -r requirements.txt` and ensure the venv is activated. |
| Packages fail on Python 3.14 | Create the venv with 3.12: `python3.12 -m venv .venv` |

API docs: http://localhost:8000/docs  
Health: http://localhost:8000/health

Demo advisor (auto-seeded on startup):

| Field    | Value                         |
|----------|-------------------------------|
| Email    | `advisor@wealthcraft.example` |
| Password | `Advisor@123`                 |

Seed sample client:

```bash
PYTHONPATH=. python3 scripts/seed_demo_client.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## Docker (Production-ready)

```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- PostgreSQL: localhost:5432

Set `SECRET_KEY` in the environment before production deployment.

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register advisor |
| POST | `/api/v1/auth/login` | JWT login |
| GET | `/api/v1/clients` | List clients |
| POST | `/api/v1/clients` | Create client profile |
| PUT | `/api/v1/clients/{id}` | Update profile |
| POST | `/api/v1/planning/preview` | Calculate plan (no files) |
| POST | `/api/v1/planning/generate` | One-click full generation |
| POST | `/api/v1/planning/what-if` | Slider adjustments |
| GET | `/api/v1/planning/risk-questionnaire` | Risk questions |
| POST | `/api/v1/planning/risk-score` | Score answers |
| GET | `/api/v1/planning/download/excel/{client_id}` | Excel download |
| GET | `/api/v1/planning/download/pdf/{client_id}` | PDF download |

Full interactive schema: `/docs` (Swagger) and `/redoc`.

---

## Configuration

All planning assumptions live in JSON (or can be extended via DB `assumption_sets`):

- `config/assumptions.json` — inflation, returns, tax limits, SWR, scenarios
- `config/investment_recommendations.json` — category allocations by risk (no scheme names hardcoded)
- `config/risk_questionnaire.json` — risk scoring bands

Environment variables: see `.env.example`.

Database:

- **Development**: SQLite (`sqlite:///./data/financial_planner.db`)
- **Production**: PostgreSQL via `DATABASE_URL=postgresql+psycopg2://...`

---

## Testing

```bash
export PYTHONPATH=.
pytest -q
```

Coverage includes TVM, loans, tax, full engine integration, Excel/PDF/chart generation.

---

## Excel Sheets Generated

Cover, Client Summary, Financial Snapshot, Income, Expenses, Assets, Liabilities, Net Worth, Cash Flow, Emergency Fund, Insurance, Investment Portfolio, Asset Allocation, Mutual Funds, Stocks, Gold, Loans, Loan Schedule, Goal Planning, Retirement, Tax Planning, Education / Marriage / Travel Planning, Estate Planning, Recommendations, Risk Analysis, Scenario Analysis, Inflation Analysis, Dashboard, Charts, Assumptions, Glossary.

---

## PDF Sections

Executive Summary → Health Scorecard → Risk → Cash Flow & Net Worth → Goals → Retirement (incl. Monte Carlo & buckets) → Investments → Insurance → Tax → Loans → Scenarios → Recommendations → 90-Day Action Plan → Estate Checklist → Appendix.

---

## Design Principles

- **No hardcoded client information** — every field is form/API driven
- **SOLID, typed, documented** Python modules
- **Indian financial planning standards** (tax slabs, 80C/80CCD/80D, HRA, EPF/NPS/PPF)
- **Configurable recommendations** — asset *categories*, not specific fund schemes

---

## License

Proprietary — for authorized advisory use. Sample data is fictional.
