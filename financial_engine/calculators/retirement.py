"""Retirement corpus, withdrawal strategy, and bucket planning."""

from __future__ import annotations

from typing import Any

from financial_engine.calculators.time_value import TimeValueCalculator
from financial_engine.models import Assets, Income


class RetirementCalculator:
    """Comprehensive retirement planner aligned with Indian wealth-management practice."""

    def __init__(self, assumptions: dict[str, Any]):
        self.assumptions = assumptions
        self.retirement_cfg = assumptions.get("retirement", {})
        self.inflation_cfg = assumptions.get("inflation", {})
        self.returns_cfg = assumptions.get("returns", {})

    def calculate(
        self,
        *,
        current_age: int,
        retirement_age: int,
        life_expectancy: int,
        current_annual_expenses: float,
        income: Income,
        assets: Assets,
        monthly_sip: float = 0.0,
        expected_return_pre: float | None = None,
        expected_return_post: float | None = None,
        inflation: float | None = None,
        healthcare_inflation: float | None = None,
        replacement_ratio: float | None = None,
        safe_withdrawal_rate: float | None = None,
        government_pension_monthly: float = 0.0,
        other_passive_monthly: float = 0.0,
    ) -> dict[str, Any]:
        years_to_retire = max(retirement_age - current_age, 0)
        years_in_retirement = max(life_expectancy - retirement_age, 1)

        inflation = inflation if inflation is not None else float(self.inflation_cfg.get("general", 0.06))
        healthcare_inflation = (
            healthcare_inflation
            if healthcare_inflation is not None
            else float(self.inflation_cfg.get("healthcare", 0.08))
        )
        replacement_ratio = (
            replacement_ratio
            if replacement_ratio is not None
            else float(self.retirement_cfg.get("pension_replacement_ratio", 0.70))
        )
        swr = (
            safe_withdrawal_rate
            if safe_withdrawal_rate is not None
            else float(self.retirement_cfg.get("safe_withdrawal_rate", 0.04))
        )
        expected_return_pre = expected_return_pre or float(
            self.returns_cfg.get("equity_flexi_cap", 0.12)
        )
        expected_return_post = expected_return_post or (
            0.6 * float(self.returns_cfg.get("equity_large_cap", 0.12))
            + 0.4 * float(self.returns_cfg.get("debt", 0.07))
        )

        # Expenses at retirement (inflation-adjusted with replacement ratio)
        annual_expense_at_retirement = TimeValueCalculator.future_value(
            current_annual_expenses * replacement_ratio, inflation, years_to_retire
        )

        # Healthcare buffer
        healthcare_base = current_annual_expenses * 0.10
        healthcare_at_retirement = TimeValueCalculator.future_value(
            healthcare_base, healthcare_inflation, years_to_retire
        )

        total_annual_need = annual_expense_at_retirement + healthcare_at_retirement

        # Passive income at retirement
        rental_at_retirement = TimeValueCalculator.future_value(
            income.annual_rental, inflation, years_to_retire
        )
        pension_annual = government_pension_monthly * 12
        other_passive_annual = other_passive_monthly * 12
        total_passive = rental_at_retirement + pension_annual + other_passive_annual

        net_annual_withdrawal_need = max(total_annual_need - total_passive, 0.0)

        # Corpus via SWR and via PV of growing annuity
        corpus_swr = TimeValueCalculator.corpus_from_withdrawal(net_annual_withdrawal_need, swr)
        real_return_post = TimeValueCalculator.real_return(expected_return_post, inflation)
        corpus_annuity = TimeValueCalculator.growing_annuity_present_value(
            net_annual_withdrawal_need,
            expected_return_post,
            inflation,
            years_in_retirement,
        )
        required_corpus = max(corpus_swr, corpus_annuity)

        # Existing retirement assets growth
        retirement_assets = assets.epf + assets.nps + assets.ppf + assets.mutual_funds * 0.6 + assets.stocks * 0.5
        other_investable = (
            assets.mutual_funds * 0.4
            + assets.stocks * 0.5
            + assets.fd
            + assets.gold * 0.5
            + assets.savings * 0.3
        )
        total_current = retirement_assets + other_investable

        fv_existing = TimeValueCalculator.future_value(
            total_current, expected_return_pre, years_to_retire
        )
        fv_sip = TimeValueCalculator.sip_future_value(monthly_sip, expected_return_pre, years_to_retire)
        # EPF ongoing contributions
        epf_monthly = income.employee_epf_contribution_monthly + income.employer_epf_contribution_monthly
        fv_epf_sip = TimeValueCalculator.sip_future_value(
            epf_monthly, float(self.returns_cfg.get("epf", 0.0815)), years_to_retire
        )

        projected_corpus = fv_existing + fv_sip + fv_epf_sip
        shortfall = max(required_corpus - projected_corpus, 0.0)
        surplus = max(projected_corpus - required_corpus, 0.0)

        additional_sip = TimeValueCalculator.sip_required_for_goal(
            required_corpus, expected_return_pre, years_to_retire, total_current
        )

        # Bucket strategy
        bucket_strategy = self._bucket_strategy(
            required_corpus, net_annual_withdrawal_need, inflation, years_in_retirement
        )

        # Sustainability: years corpus lasts at given withdrawal
        sustainability_years = self._sustainability_years(
            projected_corpus, net_annual_withdrawal_need, expected_return_post, inflation
        )

        progress = min(projected_corpus / required_corpus, 1.0) if required_corpus > 0 else 1.0

        return {
            "current_age": current_age,
            "retirement_age": retirement_age,
            "life_expectancy": life_expectancy,
            "years_to_retirement": years_to_retire,
            "years_in_retirement": years_in_retirement,
            "current_annual_expenses": round(current_annual_expenses, 2),
            "replacement_ratio": replacement_ratio,
            "inflation": inflation,
            "healthcare_inflation": healthcare_inflation,
            "annual_expense_at_retirement": round(annual_expense_at_retirement, 2),
            "healthcare_cost_at_retirement": round(healthcare_at_retirement, 2),
            "total_annual_need_at_retirement": round(total_annual_need, 2),
            "monthly_retirement_income_needed": round(total_annual_need / 12, 2),
            "passive_income_at_retirement": round(total_passive, 2),
            "net_annual_withdrawal_need": round(net_annual_withdrawal_need, 2),
            "safe_withdrawal_rate": swr,
            "required_corpus_swr": round(corpus_swr, 2),
            "required_corpus_annuity": round(corpus_annuity, 2),
            "required_corpus": round(required_corpus, 2),
            "current_retirement_assets": round(total_current, 2),
            "projected_corpus": round(projected_corpus, 2),
            "projected_from_existing": round(fv_existing, 2),
            "projected_from_sip": round(fv_sip, 2),
            "projected_from_epf_contributions": round(fv_epf_sip, 2),
            "shortfall": round(shortfall, 2),
            "surplus": round(surplus, 2),
            "additional_monthly_sip_required": round(additional_sip, 2),
            "progress_percent": round(progress * 100, 2),
            "expected_return_pre_retirement": expected_return_pre,
            "expected_return_post_retirement": expected_return_post,
            "real_return_post_retirement": round(real_return_post, 4),
            "corpus_sustainability_years": sustainability_years,
            "bucket_strategy": bucket_strategy,
            "withdrawal_strategy": {
                "method": "Safe Withdrawal Rate with Bucket Approach",
                "initial_annual_withdrawal": round(net_annual_withdrawal_need, 2),
                "initial_monthly_withdrawal": round(net_annual_withdrawal_need / 12, 2),
                "annual_step_up": inflation,
                "notes": (
                    "Withdraw from Bucket 1 (liquid/debt) for years 1-3; "
                    "refill from Bucket 2 (hybrid/balanced); "
                    "Bucket 3 (equity) for long-term growth."
                ),
            },
            "pension_sources": {
                "government_pension_annual": round(pension_annual, 2),
                "nps_estimated": round(
                    TimeValueCalculator.future_value(
                        assets.nps, float(self.returns_cfg.get("nps_equity", 0.12)), years_to_retire
                    ),
                    2,
                ),
                "epf_estimated": round(
                    TimeValueCalculator.future_value(
                        assets.epf, float(self.returns_cfg.get("epf", 0.0815)), years_to_retire
                    )
                    + fv_epf_sip,
                    2,
                ),
                "rental_income_annual": round(rental_at_retirement, 2),
                "other_passive_annual": round(other_passive_annual, 2),
            },
        }

    def _bucket_strategy(
        self,
        corpus: float,
        annual_need: float,
        inflation: float,
        years_in_retirement: int,
    ) -> dict[str, Any]:
        bucket1 = annual_need * 3  # 3 years expenses in liquid/debt
        bucket2 = annual_need * 5 * ((1 + inflation) ** 3)  # years 4-8
        bucket3 = max(corpus - bucket1 - bucket2, 0.0)
        total = bucket1 + bucket2 + bucket3 or 1.0
        return {
            "bucket_1_liquidity": {
                "amount": round(bucket1, 2),
                "allocation_percent": round(bucket1 / total * 100, 2),
                "instruments": ["Liquid Funds", "Arbitrage Funds", "Short-term Debt", "FD"],
                "purpose": "Years 1-3 living expenses",
            },
            "bucket_2_income": {
                "amount": round(bucket2, 2),
                "allocation_percent": round(bucket2 / total * 100, 2),
                "instruments": ["Hybrid Funds", "Corporate Bonds", "Conservative Hybrid"],
                "purpose": "Years 4-8 income bridge",
            },
            "bucket_3_growth": {
                "amount": round(bucket3, 2),
                "allocation_percent": round(bucket3 / total * 100, 2),
                "instruments": ["Large Cap", "Flexi Cap", "International Equity", "REITs"],
                "purpose": f"Long-term growth for years 9-{years_in_retirement}",
            },
        }

    @staticmethod
    def _sustainability_years(
        corpus: float,
        annual_withdrawal: float,
        return_rate: float,
        inflation: float,
        max_years: int = 60,
    ) -> int:
        """Simulate year-by-year drawdown until corpus depletes."""
        if corpus <= 0 or annual_withdrawal <= 0:
            return 0
        balance = corpus
        withdrawal = annual_withdrawal
        for year in range(1, max_years + 1):
            balance = balance * (1 + return_rate) - withdrawal
            if balance <= 0:
                return year
            withdrawal *= 1 + inflation
        return max_years
