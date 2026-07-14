"""
Professional Financial Planner — FastAPI application entrypoint.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from backend.auth import get_user_by_email, hash_password
from backend.routers import auth, clients, planning
from config.settings import get_settings
from database.models import User
from database.session import SessionLocal, init_db
from utils.logging_config import setup_logging

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


def _seed_demo_advisor() -> None:
    """Create a demo advisor account if none exists (credentials in README)."""
    db = SessionLocal()
    try:
        if not get_user_by_email(db, "advisor@wealthcraft.example"):
            user = User(
                email="advisor@wealthcraft.example",
                hashed_password=hash_password("Advisor@123"),
                full_name="Demo Advisor",
                role="advisor",
            )
            db.add(user)
            db.commit()
            logger.info("Seeded demo advisor: advisor@wealthcraft.example")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.reports_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.charts_dir).mkdir(parents=True, exist_ok=True)
    Path(__file__).resolve().parents[1].joinpath("data").mkdir(parents=True, exist_ok=True)
    init_db()
    _seed_demo_advisor()
    logger.info("Application started — %s", settings.app_name)
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.app_name,
    description=(
        "Enterprise-grade Professional Financial Planning System. "
        "Generate complete financial plans, Excel workbooks, and PDF reports "
        "for any client using configurable inputs — no hardcoded personal data."
    ),
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(clients.router, prefix=settings.api_prefix)
app.include_router(planning.router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "api": settings.api_prefix,
        "firm": settings.advisor_firm_name,
    }
