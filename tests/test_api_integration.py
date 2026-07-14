"""API integration tests — run with: pytest tests/test_api_integration.py -q"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from financial_engine.engine import FinancialPlanningEngine
from financial_engine.models import ClientFinancialProfile

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client: TestClient):
    email = f"apitest_{uuid.uuid4().hex[:10]}@wealthcraft.example"
    password = "TestPass@123"
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "API Tester"},
    )
    assert reg.status_code in (200, 201), reg.text
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_client_create_rejects_missing_mandatory_fields(client: TestClient, auth_headers):
    """Backend validation: name, income, and living expenses are required."""
    bad = {
        "profile": {
            "personal": {"full_name": "", "age": 30, "retirement_age": 60},
            "income": {"salary_monthly": 0},
            "expenses": {"monthly_living": 0},
            "risk_profile": "moderate",
        }
    }
    res = client.post("/api/v1/clients", headers=auth_headers, json=bad)
    assert res.status_code == 422


def test_demo_profile_uses_percentages(client: TestClient, auth_headers):
    res = client.get("/api/v1/planning/demo-profile", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "Mehta" in data["personal"]["full_name"]
    assert data["loans"][0]["interest_rate_annual"] > 1  # 8.6 not 0.086
    assert data["investments"][0]["expected_return"] >= 6
    assert data["assumptions"]["general_inflation"] == 6
    assert len(data["goals"]) >= 5
    assert len(data["loans"]) >= 3


def test_seed_demo_and_preview(client: TestClient, auth_headers):
    seed = client.post("/api/v1/planning/seed-demo-client", headers=auth_headers)
    assert seed.status_code == 200
    client_id = seed.json()["id"]

    clients = client.get("/api/v1/clients", headers=auth_headers)
    assert clients.status_code == 200
    assert any(c["id"] == client_id for c in clients.json())

    profile = client.get(f"/api/v1/clients/{client_id}", headers=auth_headers).json()["profile_data"]
    preview = client.post("/api/v1/planning/preview", headers=auth_headers, json=profile)
    assert preview.status_code == 200, preview.text
    plan = preview.json()
    assert plan["net_worth"]["net_worth"] > 0
    assert plan["health_score"]["score"] > 0
    assert plan["retirement"]["required_corpus"] > 0
    assert len(plan["goals"]) >= 3
    assert len(plan["loans"]) >= 2


def test_generate_reports(client: TestClient, auth_headers):
    seed = client.post("/api/v1/planning/seed-demo-client", headers=auth_headers).json()
    res = client.post(
        "/api/v1/planning/generate",
        headers=auth_headers,
        json={
            "client_id": seed["id"],
            "generate_excel": True,
            "generate_pdf": True,
            "generate_charts": True,
            "save": True,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["plan"]["summary"]["net_worth"] > 0
    assert body.get("excel_path")
    assert body.get("pdf_path")
    assert Path(body["excel_path"]).exists()
    assert Path(body["pdf_path"]).exists()
    assert len(body.get("chart_paths", [])) >= 1


def test_what_if_income_increase(client: TestClient, auth_headers):
    profile = json.loads((ROOT / "sample_data" / "demo_client.json").read_text())
    base = client.post("/api/v1/planning/preview", headers=auth_headers, json=profile).json()
    adjusted = client.post(
        "/api/v1/planning/what-if",
        headers=auth_headers,
        json={
            "profile": profile,
            "income_change_percent": 25,
            "expense_change_percent": 0,
            "sip_change_absolute": 0,
            "inflation_override": 0.06,
            "returns_override": 0.12,
        },
    ).json()
    assert adjusted["cash_flow"]["monthly_income"] > base["cash_flow"]["monthly_income"]


def test_risk_questionnaire(client: TestClient, auth_headers):
    q = client.get("/api/v1/planning/risk-questionnaire", headers=auth_headers)
    assert q.status_code == 200
    assert len(q.json()["questions"]) == 10
    answers = {item["id"]: "c" for item in q.json()["questions"]}
    scored = client.post("/api/v1/planning/risk-score", headers=auth_headers, json=answers)
    assert scored.status_code == 200
    assert scored.json()["profile"] in ("conservative", "moderate", "aggressive")


def test_percent_loan_rate_in_engine():
    """Engine must interpret 8.5 as 8.5%, producing a sensible EMI interest."""
    profile = ClientFinancialProfile.from_dict(
        {
            "personal": {"full_name": "Rate Test", "age": 35, "retirement_age": 60},
            "income": {"salary_monthly": 100000},
            "expenses": {"monthly_living": 40000},
            "loans": [
                {
                    "name": "Home",
                    "loan_type": "home",
                    "principal_outstanding": 1000000,
                    "interest_rate_annual": 8.5,
                    "emi": 10000,
                    "tenure_months_remaining": 120,
                }
            ],
            "assets": {"savings": 100000, "emergency_fund": 50000},
            "risk_profile": "moderate",
        }
    )
    assert abs(profile.loans[0].interest_rate_annual - 0.085) < 1e-9
    plan = FinancialPlanningEngine(config_dir=ROOT / "config").generate_plan(profile)
    assert plan.loans[0]["total_interest_without_prepayment"] > 0


def test_demo_client_end_to_end_engine():
    data = json.loads((ROOT / "sample_data" / "demo_client.json").read_text())
    profile = ClientFinancialProfile.from_dict(data)
    # Percentages converted
    assert profile.loans[0].interest_rate_annual < 1
    assert profile.investments[0].expected_return < 1
    assert profile.assumptions.general_inflation == pytest.approx(0.06)
    plan = FinancialPlanningEngine(config_dir=ROOT / "config").generate_plan(profile)
    assert plan.summary["client_name"]
    assert plan.cash_flow["monthly_surplus"] != 0 or plan.cash_flow["monthly_income"] > 0
    assert "monte_carlo" in plan.retirement
