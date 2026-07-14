"""Scenario and what-if analysis engines."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from financial_engine.models import ClientFinancialProfile


class ScenarioAnalyzer:
    """Best / Expected / Worst case scenario runner."""

    def __init__(self, assumptions: dict[str, Any]):
        self.scenario_cfg = assumptions.get("scenarios", {})

    def build_profile_variant(
        self,
        profile: ClientFinancialProfile,
        scenario_name: str,
    ) -> ClientFinancialProfile:
        cfg = self.scenario_cfg.get(scenario_name, self.scenario_cfg.get("expected_case", {}))
        variant = deepcopy(profile)

        # Adjust assumptions
        base_inflation = profile.assumptions.general_inflation
        if base_inflation is None:
            base_inflation = 0.06
        multiplier = float(cfg.get("inflation_multiplier", 1.0))
        returns_mult = float(cfg.get("returns_multiplier", 1.0))

        variant.assumptions.general_inflation = base_inflation * multiplier
        if variant.assumptions.expected_equity_return is not None:
            variant.assumptions.expected_equity_return *= returns_mult
        else:
            variant.assumptions.expected_equity_return = 0.12 * returns_mult

        variant.assumptions.salary_growth_rate = float(cfg.get("salary_growth", 0.08))

        # Scale income for salary growth perception in scenario label context
        # (used by retirement projections via assumption overrides)
        return variant

    def run_all(
        self,
        profile: ClientFinancialProfile,
        plan_fn: Callable[[ClientFinancialProfile], Any],
    ) -> dict[str, Any]:
        results = {}
        for name in ("best_case", "expected_case", "worst_case"):
            variant = self.build_profile_variant(profile, name)
            plan = plan_fn(variant)
            results[name] = {
                "assumptions": {
                    "salary_growth": self.scenario_cfg.get(name, {}).get("salary_growth"),
                    "inflation_multiplier": self.scenario_cfg.get(name, {}).get(
                        "inflation_multiplier"
                    ),
                    "returns_multiplier": self.scenario_cfg.get(name, {}).get(
                        "returns_multiplier"
                    ),
                },
                "net_worth": plan.net_worth.get("net_worth"),
                "monthly_surplus": plan.cash_flow.get("monthly_surplus"),
                "required_retirement_corpus": plan.retirement.get("required_corpus"),
                "projected_retirement_corpus": plan.retirement.get("projected_corpus"),
                "retirement_shortfall": plan.retirement.get("shortfall"),
                "health_score": plan.health_score.get("score"),
                "total_tax": plan.tax.get("recommended_regime")
                and plan.tax.get(f"{plan.tax['recommended_regime']}_regime", {}).get("total_tax"),
            }
        return results


class WhatIfAnalyzer:
    """Interactive what-if adjustments via percentage/absolute sliders."""

    @staticmethod
    def apply_adjustments(
        profile: ClientFinancialProfile,
        *,
        income_change_percent: float = 0.0,
        expense_change_percent: float = 0.0,
        sip_change_absolute: float = 0.0,
        inflation_override: float | None = None,
        returns_override: float | None = None,
        loan_interest_change_percent: float = 0.0,
        retirement_age_override: int | None = None,
    ) -> ClientFinancialProfile:
        variant = deepcopy(profile)

        factor_inc = 1 + income_change_percent / 100
        variant.income.salary_monthly *= factor_inc
        variant.income.bonus_annual *= factor_inc
        variant.income.business_income_annual *= factor_inc
        variant.income.rental_income_monthly *= factor_inc
        variant.income.other_income_annual *= factor_inc

        factor_exp = 1 + expense_change_percent / 100
        variant.expenses.monthly_living *= factor_exp
        variant.expenses.travel_monthly *= factor_exp
        variant.expenses.medical_monthly *= factor_exp
        variant.expenses.education_monthly *= factor_exp
        variant.expenses.entertainment_monthly *= factor_exp
        variant.expenses.miscellaneous_monthly *= factor_exp
        variant.expenses.rent_monthly *= factor_exp

        if variant.investments and sip_change_absolute != 0:
            # Distribute SIP change across investments
            n = len(variant.investments)
            for inv in variant.investments:
                inv.monthly_sip = max(inv.monthly_sip + sip_change_absolute / n, 0.0)
        elif sip_change_absolute != 0:
            from financial_engine.models import Investment

            variant.investments.append(
                Investment(
                    name="What-If SIP",
                    category="mutual_funds",
                    amount=0,
                    monthly_sip=max(sip_change_absolute, 0.0),
                )
            )

        if inflation_override is not None:
            variant.assumptions.general_inflation = inflation_override
        if returns_override is not None:
            variant.assumptions.expected_equity_return = returns_override

        if loan_interest_change_percent != 0:
            factor_loan = 1 + loan_interest_change_percent / 100
            for loan in variant.loans:
                loan.interest_rate_annual *= factor_loan

        if retirement_age_override is not None:
            variant.personal.retirement_age = retirement_age_override

        return variant
