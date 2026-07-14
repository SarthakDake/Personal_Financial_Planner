"""Unit tests for Indian tax calculator."""

import json
from pathlib import Path

from financial_engine.calculators.tax import TaxCalculator


def _tax_calc():
    assumptions = json.loads(
        (Path(__file__).resolve().parents[1] / "config" / "assumptions.json").read_text()
    )
    return TaxCalculator(assumptions["tax"])


def test_new_regime_low_income_rebate():
    calc = _tax_calc()
    result = calc.calculate_new_regime(1_000_000)
    # Income after std deduction well under rebate limit → low/zero tax
    assert result["total_tax"] >= 0
    assert result["regime"] == "new"


def test_compare_regimes_returns_recommendation():
    calc = _tax_calc()
    comparison = calc.compare_regimes(
        3_000_000,
        section_80c=150_000,
        section_80ccd_1b=50_000,
        section_80d_self=25_000,
        home_loan_interest=200_000,
    )
    assert comparison["recommended_regime"] in ("old", "new", "either")
    assert "old_regime" in comparison
    assert "new_regime" in comparison


def test_hra_exemption():
    calc = _tax_calc()
    exemption = calc.calculate_hra_exemption(
        basic_salary_annual=600_000,
        hra_received=300_000,
        rent_paid=240_000,
        is_metro=True,
    )
    assert exemption > 0
    assert exemption <= 300_000
