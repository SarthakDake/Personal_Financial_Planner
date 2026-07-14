"""Indian income tax planner — Old vs New regime (FY 2025-26 / AY 2026-27)."""

from __future__ import annotations

from typing import Any


class TaxCalculator:
    """
    Computes tax under Old and New regimes per Indian Income Tax rules.

    Slabs reflect Finance Act updates applicable for FY 2025-26.
    Configuration values (limits, cess) are injected from assumptions JSON.
    """

    # New regime slabs (FY 2025-26)
    NEW_REGIME_SLABS: list[tuple[float, float]] = [
        (400000, 0.00),
        (800000, 0.05),
        (1200000, 0.10),
        (1600000, 0.15),
        (2000000, 0.20),
        (2400000, 0.25),
        (float("inf"), 0.30),
    ]

    # Old regime slabs
    OLD_REGIME_SLABS: list[tuple[float, float]] = [
        (250000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float("inf"), 0.30),
    ]

    OLD_REGIME_SLABS_SENIOR: list[tuple[float, float]] = [
        (300000, 0.00),
        (500000, 0.05),
        (1000000, 0.20),
        (float("inf"), 0.30),
    ]

    def __init__(self, tax_config: dict[str, Any]):
        self.config = tax_config

    def _tax_from_slabs(self, taxable_income: float, slabs: list[tuple[float, float]]) -> float:
        if taxable_income <= 0:
            return 0.0
        tax = 0.0
        prev_limit = 0.0
        for limit, rate in slabs:
            taxable_in_slab = min(taxable_income, limit) - prev_limit
            if taxable_in_slab > 0:
                tax += taxable_in_slab * rate
            if taxable_income <= limit:
                break
            prev_limit = limit
        return tax

    def calculate_hra_exemption(
        self,
        basic_salary_annual: float,
        hra_received: float,
        rent_paid: float,
        is_metro: bool,
    ) -> float:
        """Least of: actual HRA, rent - 10% basic, 50%/40% of basic."""
        if hra_received <= 0 or rent_paid <= 0 or basic_salary_annual <= 0:
            return 0.0
        metro_rate = float(self.config.get("hra_metro_rate", 0.50))
        non_metro_rate = float(self.config.get("hra_non_metro_rate", 0.40))
        percent_basic = basic_salary_annual * (metro_rate if is_metro else non_metro_rate)
        rent_minus_10 = max(rent_paid - 0.10 * basic_salary_annual, 0.0)
        return min(hra_received, rent_minus_10, percent_basic)

    def calculate_old_regime(
        self,
        gross_income: float,
        *,
        basic_salary_annual: float = 0.0,
        hra_received: float = 0.0,
        rent_paid: float = 0.0,
        is_metro: bool = True,
        section_80c: float = 0.0,
        section_80ccd_1b: float = 0.0,
        section_80d_self: float = 0.0,
        section_80d_parents: float = 0.0,
        home_loan_interest: float = 0.0,
        is_senior: bool = False,
        parents_senior: bool = False,
        other_deductions: float = 0.0,
        ltcg_equity: float = 0.0,
        stcg_equity: float = 0.0,
    ) -> dict[str, Any]:
        std_deduction = float(self.config.get("standard_deduction_old", 50000))
        hra_exemption = self.calculate_hra_exemption(
            basic_salary_annual or gross_income * 0.4, hra_received, rent_paid, is_metro
        )

        limit_80c = float(self.config.get("section_80c_limit", 150000))
        limit_80ccd = float(self.config.get("section_80ccd_1b_limit", 50000))
        self_80d_limit = float(
            self.config.get(
                "section_80d_self_senior_limit" if is_senior else "section_80d_self_limit",
                50000 if is_senior else 25000,
            )
        )
        parents_80d_limit = float(
            self.config.get(
                "section_80d_parents_senior_limit" if parents_senior else "section_80d_parents_limit",
                50000 if parents_senior else 25000,
            )
        )
        home_loan_limit = float(self.config.get("home_loan_interest_self_occupied", 200000))

        ded_80c = min(section_80c, limit_80c)
        ded_80ccd = min(section_80ccd_1b, limit_80ccd)
        ded_80d = min(section_80d_self, self_80d_limit) + min(section_80d_parents, parents_80d_limit)
        ded_home = min(home_loan_interest, home_loan_limit)

        total_deductions = (
            std_deduction + hra_exemption + ded_80c + ded_80ccd + ded_80d + ded_home + other_deductions
        )
        taxable = max(gross_income - total_deductions, 0.0)

        slabs = self.OLD_REGIME_SLABS_SENIOR if is_senior else self.OLD_REGIME_SLABS
        base_tax = self._tax_from_slabs(taxable, slabs)

        rebate_limit = float(self.config.get("rebate_87a_old_limit", 500000))
        rebate_amount = float(self.config.get("rebate_87a_old_amount", 12500))
        rebate = min(base_tax, rebate_amount) if taxable <= rebate_limit else 0.0
        tax_after_rebate = max(base_tax - rebate, 0.0)

        # Capital gains taxed separately
        ltcg_exemption = float(self.config.get("ltcg_equity_exemption", 125000))
        ltcg_rate = float(self.config.get("ltcg_equity_rate", 0.125))
        stcg_rate = float(self.config.get("stcg_equity_rate", 0.20))
        ltcg_tax = max(ltcg_equity - ltcg_exemption, 0.0) * ltcg_rate
        stcg_tax = max(stcg_equity, 0.0) * stcg_rate

        tax_before_cess = tax_after_rebate + ltcg_tax + stcg_tax
        cess = tax_before_cess * float(self.config.get("cess_rate", 0.04))
        total_tax = tax_before_cess + cess

        return {
            "regime": "old",
            "gross_income": round(gross_income, 2),
            "standard_deduction": round(std_deduction, 2),
            "hra_exemption": round(hra_exemption, 2),
            "section_80c": round(ded_80c, 2),
            "section_80ccd_1b": round(ded_80ccd, 2),
            "section_80d": round(ded_80d, 2),
            "home_loan_interest_deduction": round(ded_home, 2),
            "other_deductions": round(other_deductions, 2),
            "total_deductions": round(total_deductions, 2),
            "taxable_income": round(taxable, 2),
            "tax_before_rebate": round(base_tax, 2),
            "rebate_87a": round(rebate, 2),
            "ltcg_tax": round(ltcg_tax, 2),
            "stcg_tax": round(stcg_tax, 2),
            "cess": round(cess, 2),
            "total_tax": round(total_tax, 2),
            "effective_tax_rate": round(total_tax / gross_income, 4) if gross_income > 0 else 0.0,
        }

    def calculate_new_regime(
        self,
        gross_income: float,
        *,
        ltcg_equity: float = 0.0,
        stcg_equity: float = 0.0,
        employer_nps: float = 0.0,
    ) -> dict[str, Any]:
        std_deduction = float(self.config.get("standard_deduction_new", 75000))
        # New regime: limited deductions — standard deduction + employer NPS (80CCD(2))
        total_deductions = std_deduction + max(employer_nps, 0.0)
        taxable = max(gross_income - total_deductions, 0.0)

        base_tax = self._tax_from_slabs(taxable, self.NEW_REGIME_SLABS)

        rebate_limit = float(self.config.get("rebate_87a_new_limit", 1200000))
        rebate_amount = float(self.config.get("rebate_87a_new_amount", 60000))
        # Full rebate if taxable income <= 12L under new regime (simplified)
        rebate = min(base_tax, rebate_amount) if taxable <= rebate_limit else 0.0
        tax_after_rebate = max(base_tax - rebate, 0.0)

        ltcg_exemption = float(self.config.get("ltcg_equity_exemption", 125000))
        ltcg_rate = float(self.config.get("ltcg_equity_rate", 0.125))
        stcg_rate = float(self.config.get("stcg_equity_rate", 0.20))
        ltcg_tax = max(ltcg_equity - ltcg_exemption, 0.0) * ltcg_rate
        stcg_tax = max(stcg_equity, 0.0) * stcg_rate

        tax_before_cess = tax_after_rebate + ltcg_tax + stcg_tax
        cess = tax_before_cess * float(self.config.get("cess_rate", 0.04))
        total_tax = tax_before_cess + cess

        return {
            "regime": "new",
            "gross_income": round(gross_income, 2),
            "standard_deduction": round(std_deduction, 2),
            "employer_nps_deduction": round(employer_nps, 2),
            "total_deductions": round(total_deductions, 2),
            "taxable_income": round(taxable, 2),
            "tax_before_rebate": round(base_tax, 2),
            "rebate_87a": round(rebate, 2),
            "ltcg_tax": round(ltcg_tax, 2),
            "stcg_tax": round(stcg_tax, 2),
            "cess": round(cess, 2),
            "total_tax": round(total_tax, 2),
            "effective_tax_rate": round(total_tax / gross_income, 4) if gross_income > 0 else 0.0,
        }

    def compare_regimes(self, gross_income: float, **kwargs: Any) -> dict[str, Any]:
        old = self.calculate_old_regime(gross_income, **kwargs)
        new = self.calculate_new_regime(
            gross_income,
            ltcg_equity=kwargs.get("ltcg_equity", 0.0),
            stcg_equity=kwargs.get("stcg_equity", 0.0),
        )
        savings = abs(old["total_tax"] - new["total_tax"])
        recommended = "old" if old["total_tax"] < new["total_tax"] else "new"
        if abs(old["total_tax"] - new["total_tax"]) < 1:
            recommended = "either"

        return {
            "old_regime": old,
            "new_regime": new,
            "recommended_regime": recommended,
            "tax_savings_by_switching": round(savings, 2),
            "recommendation_text": (
                f"The {recommended.upper()} tax regime results in lower tax liability "
                f"with savings of ₹{savings:,.0f}."
                if recommended != "either"
                else "Both regimes result in approximately the same tax."
            ),
        }
