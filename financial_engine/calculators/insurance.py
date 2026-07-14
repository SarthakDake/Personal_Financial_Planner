"""Insurance need analysis — HLV, income replacement, gap analysis."""

from __future__ import annotations

from typing import Any

from financial_engine.calculators.time_value import TimeValueCalculator
from financial_engine.models import Insurance, PersonalDetails


class InsuranceCalculator:
    """Human Life Value and insurance adequacy analysis."""

    def __init__(self, assumptions: dict[str, Any]):
        self.cfg = assumptions.get("insurance", {})

    def human_life_value(
        self,
        annual_income: float,
        annual_personal_expenses: float,
        years_to_retirement: int,
        discount_rate: float = 0.06,
        income_growth: float = 0.05,
    ) -> float:
        """
        HLV = PV of future earnings attributable to dependents.

        Uses growing annuity of (income - personal expenses).
        """
        annual_contribution = max(annual_income - annual_personal_expenses, 0.0)
        if years_to_retirement <= 0:
            return 0.0
        return TimeValueCalculator.growing_annuity_present_value(
            annual_contribution, discount_rate, income_growth, years_to_retirement
        )

    def income_replacement_need(
        self,
        annual_income: float,
        multiple: float | None = None,
    ) -> float:
        multiple = multiple if multiple is not None else float(self.cfg.get("life_cover_multiple", 15))
        return annual_income * multiple

    def analyze(
        self,
        *,
        personal: PersonalDetails,
        annual_income: float,
        annual_expenses: float,
        outstanding_liabilities: float,
        existing_insurance: Insurance,
        goals_funding_gap: float = 0.0,
    ) -> dict[str, Any]:
        years_to_retire = max(personal.retirement_age - personal.age, 0)
        personal_expense_share = annual_expenses * 0.30  # approx personal consumption

        hlv = self.human_life_value(annual_income, personal_expense_share, years_to_retire)
        income_replacement = self.income_replacement_need(annual_income)

        # Recommended life cover = max(HLV, income replacement) + liabilities + goals - existing assets adjustment
        recommended_life = max(hlv, income_replacement) + outstanding_liabilities + goals_funding_gap * 0.5
        life_gap = max(recommended_life - existing_insurance.life_cover, 0.0)

        health_min = float(self.cfg.get("health_cover_minimum", 1000000))
        # Scale health cover with dependents and city
        health_recommended = health_min * (1 + 0.25 * personal.dependents)
        if personal.city_type == "metro":
            health_recommended *= 1.5
        health_gap = max(health_recommended - existing_insurance.health_cover, 0.0)

        ci_min = float(self.cfg.get("critical_illness_minimum", 2500000))
        ci_recommended = max(ci_min, annual_income * 3)
        ci_gap = max(ci_recommended - existing_insurance.critical_illness_cover, 0.0)

        accident_min = float(self.cfg.get("accident_cover_minimum", 5000000))
        accident_recommended = max(accident_min, annual_income * 5)
        accident_gap = max(accident_recommended - existing_insurance.accident_cover, 0.0)

        total_premium = (
            existing_insurance.health_premium_annual
            + existing_insurance.life_premium_annual
            + existing_insurance.accident_premium_annual
            + existing_insurance.critical_illness_premium_annual
        )
        premium_to_income = total_premium / annual_income if annual_income > 0 else 0.0

        return {
            "human_life_value": round(hlv, 2),
            "income_replacement_need": round(income_replacement, 2),
            "outstanding_liabilities": round(outstanding_liabilities, 2),
            "life": {
                "existing_cover": round(existing_insurance.life_cover, 2),
                "recommended_cover": round(recommended_life, 2),
                "gap": round(life_gap, 2),
                "adequate": life_gap <= 0,
                "premium_annual": round(existing_insurance.life_premium_annual, 2),
            },
            "health": {
                "existing_cover": round(existing_insurance.health_cover, 2),
                "recommended_cover": round(health_recommended, 2),
                "gap": round(health_gap, 2),
                "adequate": health_gap <= 0,
                "premium_annual": round(existing_insurance.health_premium_annual, 2),
            },
            "critical_illness": {
                "existing_cover": round(existing_insurance.critical_illness_cover, 2),
                "recommended_cover": round(ci_recommended, 2),
                "gap": round(ci_gap, 2),
                "adequate": ci_gap <= 0,
                "premium_annual": round(existing_insurance.critical_illness_premium_annual, 2),
            },
            "accident": {
                "existing_cover": round(existing_insurance.accident_cover, 2),
                "recommended_cover": round(accident_recommended, 2),
                "gap": round(accident_gap, 2),
                "adequate": accident_gap <= 0,
                "premium_annual": round(existing_insurance.accident_premium_annual, 2),
            },
            "total_premium_annual": round(total_premium, 2),
            "premium_to_income_ratio": round(premium_to_income, 4),
            "recommendations": self._recommendations(life_gap, health_gap, ci_gap, accident_gap),
        }

    @staticmethod
    def _recommendations(life_gap: float, health_gap: float, ci_gap: float, accident_gap: float) -> list[str]:
        recs: list[str] = []
        if life_gap > 0:
            recs.append(
                f"Increase term life cover by approximately ₹{life_gap:,.0f}. Prefer pure term plans."
            )
        else:
            recs.append("Life cover appears adequate relative to HLV and liabilities.")
        if health_gap > 0:
            recs.append(
                f"Enhance family floater / individual health cover by ₹{health_gap:,.0f}."
            )
        else:
            recs.append("Health insurance cover meets minimum recommended levels.")
        if ci_gap > 0:
            recs.append(f"Consider critical illness cover of ₹{ci_gap:,.0f} additional.")
        if accident_gap > 0:
            recs.append(f"Add personal accident cover of approximately ₹{accident_gap:,.0f}.")
        return recs
