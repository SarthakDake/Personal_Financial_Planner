#!/usr/bin/env python3
"""
Manual / CI-friendly end-to-end checks you can run anytime:

    PYTHONPATH=. python3 scripts/run_manual_checks.py

Exits non-zero if any check fails.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from financial_engine.engine import FinancialPlanningEngine
from financial_engine.models import ClientFinancialProfile
from utils.percent import convert_profile_rates_to_decimal, percent_to_decimal


def check(name: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    return condition


def main() -> int:
    ok = True
    demo_path = ROOT / "sample_data" / "demo_client.json"
    data = json.loads(demo_path.read_text())

    ok &= check("Demo profile file exists", demo_path.exists())
    ok &= check("Demo has multi-loan real-life scenario", len(data.get("loans", [])) >= 3)
    ok &= check("Demo has multiple goals", len(data.get("goals", [])) >= 5)
    ok &= check(
        "Loan rates stored as percentages",
        data["loans"][0]["interest_rate_annual"] > 1,
        f"got {data['loans'][0]['interest_rate_annual']}",
    )
    ok &= check(
        "Investment returns stored as percentages",
        data["investments"][0]["expected_return"] > 1,
        f"got {data['investments'][0]['expected_return']}",
    )
    ok &= check("percent_to_decimal(8.5) == 0.085", percent_to_decimal(8.5) == 0.085)

    converted = convert_profile_rates_to_decimal(data)
    ok &= check(
        "Conversion yields decimal loan rate",
        abs(converted["loans"][0]["interest_rate_annual"] - data["loans"][0]["interest_rate_annual"] / 100)
        < 1e-9,
    )

    engine = FinancialPlanningEngine(config_dir=ROOT / "config")
    profile = ClientFinancialProfile.from_dict(data)
    plan = engine.generate_plan(profile)
    plan_dict = engine.plan_to_dict(plan)

    ok &= check("Plan net worth positive", plan.net_worth["net_worth"] > 0, str(plan.net_worth["net_worth"]))
    ok &= check("Health score computed", plan.health_score["score"] > 0, str(plan.health_score["score"]))
    ok &= check("Retirement corpus computed", plan.retirement["required_corpus"] > 0)
    ok &= check("Tax recommendation present", plan.tax["recommended_regime"] in ("old", "new", "either"))
    ok &= check("Goals planned", len(plan.goals) >= 5)
    ok &= check("Monte Carlo attached", "monte_carlo" in plan.retirement)
    ok &= check("Priority actions generated", len(plan.recommendations["priority_actions"]) >= 1)

    # Lightweight report generation
    from charts.generator import ChartGenerator
    from excel_generator.workbook import ExcelReportGenerator
    from pdf_generator.report import PDFReportGenerator

    out = ROOT / "output" / "manual_checks"
    charts_dir = out / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    firm = {"name": "WealthCraft Advisors", "tagline": "Test", "email": "t@x.com", "phone": ""}
    charts = ChartGenerator(charts_dir).generate_all(plan_dict)
    excel = ExcelReportGenerator(firm).generate(plan_dict, profile, out / "plan.xlsx", charts)
    pdf = PDFReportGenerator(firm).generate(plan_dict, profile, out / "plan.pdf", charts)
    ok &= check("Charts generated", len(charts) >= 5, str(len(charts)))
    ok &= check("Excel generated", excel.exists() and excel.stat().st_size > 10000)
    ok &= check("PDF generated", pdf.exists() and pdf.stat().st_size > 10000)

    print()
    print("All checks passed." if ok else "Some checks failed.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
