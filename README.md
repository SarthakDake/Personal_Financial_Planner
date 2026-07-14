# WealthCraft — Professional Financial Planning System

Developer onboarding guide for the full stack. Use this document to understand architecture, run the app locally, find credentials, and navigate the codebase.

WealthCraft is an Indian wealth-advisory style planning platform: advisors authenticate with JWT, manage multiple clients, run a pure-Python financial engine, and generate Excel + PDF reports in one click.

---

## Table of contents

1. [Default credentials](#default-credentials)
2. [What the application does](#what-the-application-does)
3. [Tech stack](#tech-stack)
4. [Repository structure](#repository-structure)
5. [How the system works](#how-the-system-works)
6. [Prerequisites](#prerequisites)
7. [Local setup](#local-setup)
8. [Environment variables](#environment-variables)
9. [Input conventions](#input-conventions)
10. [Important product rules](#important-product-rules)
11. [API overview](#api-overview)
12. [Configuration files](#configuration-files)
13. [Reports (Excel & PDF)](#reports-excel--pdf)
14. [Data storage & security](#data-storage--security)
15. [Testing](#testing)
16. [Docker](#docker)
17. [Frontend routes](#frontend-routes)
18. [Troubleshooting](#troubleshooting)
19. [Further docs](#further-docs)

---

## Default credentials

These are **auto-seeded on backend startup** (see `backend/main.py`). Use them for local development and demos.

| Item | Value |
|------|--------|
| **Advisor email** | `advisor@wealthcraft.example` |
| **Advisor password** | `Advisor@123` |
| **Role** | `advisor` |
| **Demo client family** | Priya & Rohan Mehta (from `sample_data/demo_client.json`) |

**Load the demo client after login**

- UI: Dashboard → **Load Demo** / **Load Demo Family**
- Or CLI:

```bash
PYTHONPATH=. python3 scripts/seed_demo_client.py
```

> Change `SECRET_KEY` and demo passwords before any real deployment. Never use these credentials in production.

---

## What the application does

Advisors can:

1. Register / log in (JWT)
2. Create and edit **fully configurable** client profiles (no hardcoded personal data in the engine)
3. Preview a plan on the dashboard (net worth, allocation, goals, tax, insurance, health score)
4. Run **what-if** adjustments
5. Generate **Excel + PDF + charts** in one API call
6. Download reports per client

Financial engine coverage:

- Net worth, cash flow, savings & DTI ratios  
- Emergency fund, goal SIP / lumpsum funding  
- Retirement corpus, safe withdrawal rate, Monte Carlo, FIRE  
- EMI amortization & prepayment analysis  
- Old vs New Indian tax regimes  
- HLV / insurance gap analysis  
- Portfolio allocation & JSON-driven category recommendations  
- Scenario analysis & financial health score  

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, Recharts, React Router, Axios, Zod |
| Backend | FastAPI, SQLAlchemy, Pydantic, python-jose (JWT), bcrypt |
| Engine | Pure Python + NumPy / Pandas / SciPy |
| Excel | openpyxl / XlsxWriter |
| PDF | ReportLab + embedded DejaVu fonts (`₹` support) |
| Charts | Matplotlib (PNG for reports), Recharts (UI) |
| DB (dev) | SQLite → `data/financial_planner.db` |
| DB (prod) | PostgreSQL via Docker Compose |

**Recommended Python:** 3.11 or 3.12 (avoid 3.14 for scientific wheels).  
**Node.js:** 20+

---

## Repository structure

```text
.
├── backend/                 # FastAPI app, auth, routers, schemas
│   ├── main.py              # App entry, CORS, demo user seed
│   ├── auth.py              # JWT + bcrypt helpers
│   ├── schemas.py           # Request/response validation
│   └── routers/
│       ├── auth.py          # register / login / me
│       ├── clients.py       # multi-client CRM
│       └── planning.py      # preview, generate, what-if, downloads
├── financial_engine/        # Calculation engine (no FastAPI dependency)
│   ├── engine.py            # Orchestrates a full plan
│   ├── models.py            # Dataclasses / profile parsing
│   ├── calculators/         # TVM, tax, loans, retirement, etc.
│   ├── scenarios.py         # Best / expected / worst
│   └── risk_profiler.py
├── excel_generator/         # Multi-sheet workbook
├── pdf_generator/           # Dark neon PDF report
│   └── fonts/               # DejaVuSans — required for ₹ in PDF
├── charts/                  # Matplotlib chart generator
├── database/                # SQLAlchemy models + session
├── config/                  # JSON assumptions + settings.py
├── frontend/                # React SPA
│   └── src/
│       ├── pages/           # Landing, Login, Dashboard, Planner, …
│       ├── components/      # Layout + UI primitives
│       ├── lib/             # api.ts, validation, utils
│       └── types/           # Shared TS types + emptyProfile()
├── sample_data/             # demo_client.json (illustrative family)
├── scripts/                 # seed_demo_client, run_manual_checks
├── tests/                   # unit + API + report tests
├── docs/                    # DATA_STORAGE.md, API.md
├── deploy/                  # Nginx for Docker frontend
├── data/                    # SQLite DB (created at runtime — do not delete casually)
├── output/                  # Generated Excel / PDF / charts
├── requirements.txt
├── requirements-postgres.txt
├── docker-compose.yml
└── Dockerfile
```

---

## How the system works

```text
Browser (Vite :5173)
    │  /api/v1/*  (proxied)
    ▼
FastAPI (uvicorn :8000)
    │  JWT auth
    ├─► SQLAlchemy  →  SQLite / PostgreSQL
    └─► FinancialPlanningEngine.generate_plan(profile)
            ├─► charts.ChartGenerator
            ├─► excel_generator.ExcelReportGenerator
            └─► pdf_generator.PDFReportGenerator
```

**Typical advisor flow**

1. `POST /auth/login` → store `access_token` in `localStorage`
2. Create/update client (`/clients`) with a full `profile_data` JSON
3. `POST /planning/preview` for dashboard numbers (no files)
4. `POST /planning/generate` with `generate_excel`, `generate_pdf`, `generate_charts`, `save`
5. Download via `/planning/download/excel/{client_id}` or `/pdf/{client_id}`

**Net worth formula**

```text
Net Worth = Total Assets (Assets step) − Sum of loan principal outstanding
```

Investment SIP rows are used for cash-flow / projections; **balances for net worth come from the Assets section**. If loans are filled and assets are left at ₹0, net worth will be negative.

---

## Prerequisites

- Python 3.11 or 3.12  
- Node.js 20+ and npm  
- Git  

Optional for production-like runs: Docker + Docker Compose.

---

## Local setup

### 1. Clone & environment file

```bash
git clone <repo-url>
cd Personal_Financial_Planner   # or your local folder name
cp .env.example .env
```

### 2. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

export PYTHONPATH=.
uvicorn backend.main:app --reload --port 8000
```

| URL | Purpose |
|-----|---------|
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |

SQLite is used by default — no Postgres install required for local work.

Optional Postgres driver:

```bash
pip install -r requirements-postgres.txt
# then set DATABASE_URL in .env
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: **http://localhost:5173**

Vite proxies `/api` and `/health` to `http://localhost:8000` (see `frontend/vite.config.ts`).

### 4. First login

1. Open http://localhost:5173/login  
2. Use `advisor@wealthcraft.example` / `Advisor@123`  
3. Click **Load Demo** on the Dashboard  

---

## Environment variables

Primary file: `.env` (from `.env.example`).

| Variable | Default / notes |
|----------|-----------------|
| `SECRET_KEY` | JWT signing key — change in production |
| `DATABASE_URL` | `sqlite:///./data/financial_planner.db` |
| `API_PREFIX` | `/api/v1` |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |
| `CONFIG_DIR` | `./config` |
| `REPORTS_DIR` | `./output/reports` |
| `CHARTS_DIR` | `./output/charts` |
| `ADVISOR_FIRM_*` | Branding printed on Excel/PDF |

Frontend optional:

| Variable | Notes |
|----------|--------|
| `VITE_API_URL` | Defaults to `/api/v1` (use proxy in dev) |

---

## Input conventions

| Input type | How to enter |
|------------|----------------|
| Money | Full rupees — labels say **Monthly ₹**, **Annual ₹**, or lump-sum |
| Interest / returns / inflation | **Whole percent** — enter `8.5` for 8.5%, **not** `0.085` |
| Ages | Years (client age, retirement age, life expectancy) |
| Loan tenure | Months remaining |
| Insurance cover | Sum assured (₹); premiums are **annual** ₹ |

The UI and API accept percentages; `ClientFinancialProfile.from_dict` / `utils/percent.py` convert to decimals for engine math.

Mandatory validation (Zod + Pydantic): name, ages, income, living expenses, risk profile, and any added loans / investments / goals.

In-app glossary: `/glossary`.

---

## Important product rules

- **No hardcoded client PII** in the engine — all profiles are form/API driven.  
- Sample data in `sample_data/` is fictional.  
- Recommendations are **category-based** (`config/investment_recommendations.json`), not specific fund schemes.  
- PDF uses bundled **DejaVu** fonts so the Indian Rupee symbol `₹` renders correctly.  
- Do **not** delete `data/` while the API is running (SQLite file replace causes stale JWT / “Could not validate credentials”).  
- Theme: dark neon charcoal UI + matching dark PDF (`#0D0D0D` / cyan `#00D1FF`).

---

## API overview

Base path: `/api/v1`  
Auth header: `Authorization: Bearer <access_token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create advisor |
| POST | `/auth/login` | JSON login → JWT |
| POST | `/auth/login/form` | OAuth2 form login (Swagger Authorize) |
| GET | `/auth/me` | Current advisor |
| GET | `/clients` | List advisor’s clients |
| POST | `/clients` | Create client + profile |
| GET | `/clients/{id}` | Get client |
| PUT | `/clients/{id}` | Update profile |
| DELETE | `/clients/{id}` | Soft-delete / remove |
| POST | `/planning/preview` | Calculate plan (no files) |
| POST | `/planning/generate` | Excel + PDF + charts + optional save |
| POST | `/planning/what-if` | Scenario adjustments |
| GET | `/planning/risk-questionnaire` | Risk questions |
| POST | `/planning/risk-score` | Score answers |
| GET | `/planning/demo-profile` | Demo JSON (rates as %) |
| POST | `/planning/seed-demo-client` | Upsert demo family for logged-in advisor |
| GET | `/planning/download/excel/{client_id}` | Download latest Excel |
| GET | `/planning/download/pdf/{client_id}` | Download latest PDF |

Full schema: http://localhost:8000/docs · also see [`docs/API.md`](docs/API.md).

**Login example**

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"advisor@wealthcraft.example","password":"Advisor@123"}'
```

---

## Configuration files

| File | Purpose |
|------|---------|
| `config/assumptions.json` | Inflation, returns, tax limits, SWR, Monte Carlo, scenarios |
| `config/investment_recommendations.json` | Allocation templates by risk profile |
| `config/risk_questionnaire.json` | Questions + score bands |
| `config/settings.py` | Pydantic settings from env |

Override client-level assumptions via the profile’s `assumptions` object in the Planner.

---

## Reports (Excel & PDF)

### Excel (`excel_generator/`)

30+ sheets including Cover, Dashboard, Income/Expenses, Assets/Liabilities, Goals, Retirement, Tax, Loans, Scenarios, Recommendations, Glossary, Assumptions.

### PDF (`pdf_generator/`)

Multi-page dark-theme advisory report:

Executive Summary → Health Score → Risk → Cash Flow & Net Worth → Goals → Retirement (Monte Carlo / buckets) → Investments → Insurance → Tax → Loans → Scenarios → Recommendations → 90-Day Action Plan → Estate → Appendix.

Fonts: `pdf_generator/fonts/DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` (required for `₹`).

### Charts (`charts/`)

Matplotlib PNGs embedded in Excel/PDF (net worth, cash flow, allocation, goals, retirement, scenarios, health score).

Generated files land under `output/reports/<client_id>/` and `output/charts/<client_id>/`.

---

## Data storage & security

| Data | Location | Survives restart? |
|------|----------|-------------------|
| Advisors / clients / plans | `data/financial_planner.db` (SQLite) | Yes |
| Excel / PDF / charts | `output/` | Yes |
| Assumptions | `config/*.json` | Yes |

Security basics:

- Passwords hashed with **bcrypt**  
- API protected by **JWT** (HS256)  
- Clients scoped by `advisor_id`  
- Downloads require authentication  

Details: [`docs/DATA_STORAGE.md`](docs/DATA_STORAGE.md).

---

## Testing

```bash
export PYTHONPATH=.
pytest -q                                 # full suite
pytest tests/test_api_integration.py -q   # API only
pytest tests/test_reports.py -q           # Excel / PDF / charts (incl. ₹ check)
python3 scripts/run_manual_checks.py      # end-to-end smoke checks
```

Coverage includes TVM, loans, tax, engine integration, and report generation.

---

## Docker

```bash
# optional: export SECRET_KEY=...
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (Nginx) | http://localhost |
| Backend API | http://localhost:8000 |
| PostgreSQL | localhost:5432 (`fp_user` / `fp_password` / db `financial_planner`) |

Compose wires `DATABASE_URL` to Postgres automatically. See also [`DEPLOYMENT.md`](DEPLOYMENT.md).

---

## Frontend routes

| Path | Page |
|------|------|
| `/` | Landing |
| `/login` | Advisor login / register |
| `/dashboard` | KPIs, allocation, goals |
| `/clients` | Client list / manage |
| `/planner` | Multi-step profile wizard + generate |
| `/what-if` | Scenario sliders |
| `/glossary` | Financial terms |

Auth: `access_token` in `localStorage`. Stale tokens are cleared on `401` / fresh login.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not validate credentials` | Clear site data / log in again. Restart API if `data/financial_planner.db` was replaced while uvicorn was running. |
| `Incorrect email or password` | Use demo creds above, or register a new advisor. Demo password is reset on startup if the hash drifts. |
| Negative net worth | Assets step empty or lower than loan principals. Fill **Assets** in full ₹ (not only Investments SIPs). |
| `₹` missing / boxes in PDF | Ensure `pdf_generator/fonts/DejaVu*.ttf` exist; regenerate PDF. |
| `pg_config` / `psycopg2` build errors | Local SQLite does not need Postgres. Use `requirements.txt` only, or Python 3.12. |
| `uvicorn: command not found` | Activate `.venv` and reinstall `requirements.txt`. |
| Frontend API calls fail | Backend must be on :8000; use Vite proxy (default) or set `VITE_API_URL`. |
| Packages fail on Python 3.14 | Recreate venv with 3.12: `python3.12 -m venv .venv` |

---

## Further docs

| Doc | Contents |
|-----|----------|
| [`docs/API.md`](docs/API.md) | API request/response notes |
| [`docs/DATA_STORAGE.md`](docs/DATA_STORAGE.md) | Persistence & security |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Deployment notes |
| http://localhost:8000/docs | Live OpenAPI / Swagger |

---

## Design principles

1. **Configurable inputs only** — no hardcoded client data in calculations  
2. **Indian planning standards** — tax slabs, 80C / 80CCD / 80D, HRA, EPF / NPS / PPF  
3. **Category recommendations** — not scheme-level product pushing  
4. **Typed, modular Python** — engine separable from the web layer  
5. **Advisor-grade outputs** — Excel + multi-page PDF suitable for client discussions  

---

## License

Proprietary — for authorized advisory use. Sample data is fictional.
