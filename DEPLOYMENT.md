# Deployment Guide — WealthCraft Financial Planner

## Local Development

1. Copy `.env.example` → `.env` and set a strong `SECRET_KEY`.
2. Install Python deps: `pip install -r requirements.txt`
3. Start API: `PYTHONPATH=. uvicorn backend.main:app --reload --port 8000`
4. Start UI: `cd frontend && npm install && npm run dev`
5. Optional sample client: `PYTHONPATH=. python3 scripts/seed_demo_client.py`

## Docker Compose (recommended)

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
docker compose up --build -d
```

Services:

| Service  | URL / Port                         |
|----------|------------------------------------|
| Frontend | http://localhost                   |
| Backend  | http://localhost:8000              |
| Postgres | localhost:5432 (`fp_user` / `fp_password`) |

## PostgreSQL Production Notes

Set:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/financial_planner
APP_ENV=production
DEBUG=false
CORS_ORIGINS=https://your-domain.example
SECRET_KEY=<long-random-value>
```

Install the Postgres driver on the host/image:

```bash
pip install -r requirements-postgres.txt
```

SQLAlchemy creates tables on startup via `init_db()`. For managed migrations, Alembic is included in requirements — initialize with:

```bash
alembic init alembic   # first time only, then autogenerate revisions
```

## Reverse Proxy

`deploy/nginx.conf` proxies `/api`, `/docs`, and `/health` to the backend container and serves the SPA for all other routes.

## Security Checklist

- [ ] Rotate `SECRET_KEY`
- [ ] Change demo advisor password or disable seed user in production
- [ ] Restrict `CORS_ORIGINS`
- [ ] Use HTTPS termination
- [ ] Back up PostgreSQL volume
- [ ] Persist `/app/output/reports` and `/app/output/charts` volumes

## Health Checks

- `GET /health` → `{ "status": "ok" }`
- Swagger UI → `/docs`
