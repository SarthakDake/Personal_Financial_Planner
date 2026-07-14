"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Professional Financial Planner"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-change-in-production-use-openssl-rand"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'financial_planner.db'}"

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    config_dir: str = str(ROOT_DIR / "config")
    reports_dir: str = str(ROOT_DIR / "output" / "reports")
    charts_dir: str = str(ROOT_DIR / "output" / "charts")
    sample_data_dir: str = str(ROOT_DIR / "sample_data")

    advisor_firm_name: str = "WealthCraft Advisors"
    advisor_firm_tagline: str = "Clarity. Discipline. Prosperity."
    advisor_contact_email: str = "advisor@wealthcraft.example"
    advisor_contact_phone: str = "+91-00000-00000"

    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
