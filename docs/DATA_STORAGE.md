# Data Storage, Security & Persistence

## Where is data stored?

| Data | Location | Survives app shutdown? |
|------|----------|------------------------|
| Advisors (users) | SQLite DB file `data/financial_planner.db` | **Yes** |
| Clients & profiles | Same SQLite DB (`clients` table, JSON `profile_data`) | **Yes** |
| Generated plans | Same DB (`financial_plans` table) | **Yes** |
| Excel / PDF / charts | `output/reports/` and `output/charts/` on disk | **Yes** |
| Config assumptions | `config/*.json` in the repo | **Yes** |

Development default database URL:

```env
DATABASE_URL=sqlite:///./data/financial_planner.db
```

That creates a **file on disk** under the project’s `data/` folder. Stopping `uvicorn` or closing the laptop does **not** erase it.

**Do not delete** the `data/` folder if you want to keep clients and plans.

### Production (PostgreSQL)

With Docker Compose or a managed Postgres instance, data lives in the Postgres volume / server — also persistent across restarts.

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/financial_planner
```

---

## Is it secured?

### What is protected today

- **Passwords** are hashed with **bcrypt** (never stored in plain text).
- **API access** for clients/plans requires a **JWT** bearer token after login.
- Each advisor can only see **their own clients** (filtered by `advisor_id`).
- Generated download endpoints also require authentication.

### What you should do for real use

1. Set a strong `SECRET_KEY` in `.env` (used to sign JWTs).
2. Change the demo advisor password (`advisor@wealthcraft.example` / `Advisor@123`).
3. Use HTTPS in production (reverse proxy / load balancer).
4. Prefer PostgreSQL in production and restrict DB network access.
5. Back up `data/financial_planner.db` (or the Postgres volume) regularly.

### What is not full encryption-at-rest by default

- SQLite/Postgres store client financial JSON in the database. Disk encryption is an OS/hosting concern (FileVault, LUKS, cloud disk encryption).
- The app does not encrypt individual profile fields separately; protect the DB file and server access.

---

## Backup tips

```bash
# While the app is stopped or idle:
cp data/financial_planner.db data/backup-$(date +%Y%m%d).db

# Also back up generated reports if needed:
cp -r output/reports backups/reports-$(date +%Y%m%d)
```

---

## Summary

- Shutdown ≠ data loss — data is on disk (SQLite) or in Postgres.
- Login is required; passwords are hashed; JWTs gate the API.
- Keep the `data/` directory (and backups) safe; set `SECRET_KEY` before production use.
