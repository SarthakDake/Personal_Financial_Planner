"""Integration tests for the full financial planning engine."""

import json
from pathlib import Path

from financial_engine.engine import FinancialPlanningEngine
from financial_engine.models import ClientFinancialProfile


ROOT = Path(__file__).resolve().parents[1]


def _demo_profile() -> ClientFinancialProfile:
    data = json.loads((ROOT / "sample_data" / "demo_client.json").read_text())
    return ClientFinancialProfile.from_dict(data)


def test_generate_plan_complete():
    engine = FinancialPlanningEngine(config_dir=ROOT / "config")
    plan = engine.generate_plan(_demo_profile())
    assert plan.net_worth["net_worth"] > 0
    assert plan.cash_flow["monthly_income"] > 0
    assert plan.retirement["required_corpus"] > 0
    assert plan.health_score["score"] > 0
    assert plan.tax["recommended_regime"] in ("old", "new", "either")
    assert len(plan.goals) >= 1
    assert len(plan.recommendations["priority_actions"]) >= 1
    assert "monte_carlo" in plan.retirement
    assert plan.fire["fire_number"] > 0


def test_no_hardcoded_client_required():
    """Engine works with empty/minimal configurable profile."""
    engine = FinancialPlanningEngine(config_dir=ROOT / "config")
    profile = ClientFinancialProfile.from_dict(
        {
            "personal": {"full_name": "Test User", "age": 28, "retirement_age": 55},
            "income": {"salary_monthly": 100000},
            "expenses": {"monthly_living": 40000},
            "assets": {"savings": 200000, "emergency_fund": 100000},
            "risk_profile": "aggressive",
        }
    )
    plan = engine.generate_plan(profile)
    assert plan.summary["client_name"] == "Test User"
    assert plan.cash_flow["monthly_surplus"] > 0


def test_what_if_changes_surplus():
    engine = FinancialPlanningEngine(config_dir=ROOT / "config")
    profile = _demo_profile()
    base = engine.generate_plan(profile)
    adjusted = engine.what_if(profile, {"income_change_percent": 20})
    assert adjusted.cash_flow["monthly_income"] > base.cash_flow["monthly_income"]


def test_plan_to_dict_serializable():
    engine = FinancialPlanningEngine(config_dir=ROOT / "config")
    plan = engine.generate_plan(_demo_profile())
    data = engine.plan_to_dict(plan)
    # Ensure JSON serializable
    json.dumps(data, default=str)
    assert "summary" in data
    assert "retirement" in data
