#!/usr/bin/env python3
"""Seed the demo advisor account with the sample client profile."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.auth import get_user_by_email, hash_password  # noqa: E402
from database.models import Client, User  # noqa: E402
from database.session import SessionLocal, init_db  # noqa: E402


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        user = get_user_by_email(db, "advisor@wealthcraft.example")
        if not user:
            user = User(
                email="advisor@wealthcraft.example",
                hashed_password=hash_password("Advisor@123"),
                full_name="Demo Advisor",
                role="advisor",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        existing = (
            db.query(Client)
            .filter(Client.advisor_id == user.id, Client.full_name == "Aarav Sharma")
            .first()
        )
        profile = json.loads((ROOT / "sample_data" / "demo_client.json").read_text())
        if existing:
            existing.profile_data = profile
            existing.risk_profile = profile.get("risk_profile", "moderate")
            db.commit()
            print(f"Updated demo client: {existing.id}")
        else:
            client = Client(
                advisor_id=user.id,
                full_name=profile["personal"]["full_name"],
                email=profile["personal"].get("email", ""),
                phone=profile["personal"].get("phone", ""),
                pan=profile["personal"].get("pan", ""),
                profile_data=profile,
                risk_profile=profile.get("risk_profile", "moderate"),
                notes="Sample data for demonstration — replace with real client inputs.",
            )
            db.add(client)
            db.commit()
            db.refresh(client)
            print(f"Created demo client: {client.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
