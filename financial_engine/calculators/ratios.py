"""Financial ratios — net worth, cash flow, savings, DTI, emergency fund."""

from __future__ import annotations

from typing import Any

from financial_engine.models import Assets, Expenses, Income, RiskProfile


class RatioCalculator:
    """Core financial health ratios used by advisory firms."""

    def __init__(self, assumptions: dict[str, Any]):
        self.ef_cfg = assumptions.get("emergency_fund", {})

    def net_worth(self, assets: Assets, total_liabilities: float) -> dict[str, Any]:
        total_assets = assets.total_assets
        nw = total_assets - total_liabilities
        return {
            "total_assets": round(total_assets, 2),
            "financial_assets": round(assets.financial_assets, 2),
            "real_estate": round(assets.real_estate, 2),
            "total_liabilities": round(total_liabilities, 2),
            "net_worth": round(nw, 2),
            "financial_net_worth": round(assets.financial_assets - total_liabilities, 2),
        }

    def cash_flow(
        self,
        income: Income,
        expenses: Expenses,
        total_emi: float,
        total_sip: float = 0.0,
    ) -> dict[str, Any]:
        monthly_income = income.total_monthly_income
        monthly_expenses = expenses.total_monthly
        monthly_outflow = monthly_expenses + total_emi + total_sip
        surplus = monthly_income - monthly_outflow
        savings_before_sip = monthly_income - monthly_expenses - total_emi

        return {
            "monthly_income": round(monthly_income, 2),
            "annual_income": round(income.total_annual_income, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "annual_expenses": round(expenses.total_annual, 2),
            "monthly_emi": round(total_emi, 2),
            "monthly_sip": round(total_sip, 2),
            "monthly_outflow": round(monthly_outflow, 2),
            "monthly_surplus": round(surplus, 2),
            "annual_surplus": round(surplus * 12, 2),
            "investable_surplus": round(max(savings_before_sip, 0.0), 2),
            "expense_breakdown": {
                "living": expenses.monthly_living,
                "travel": expenses.travel_monthly,
                "medical": expenses.medical_monthly,
                "education": expenses.education_monthly,
                "insurance": expenses.insurance_premium_monthly,
                "entertainment": expenses.entertainment_monthly,
                "miscellaneous": expenses.miscellaneous_monthly,
                "rent": expenses.rent_monthly,
            },
            "income_breakdown": {
                "salary": income.salary_monthly,
                "bonus_monthly_equiv": income.bonus_annual / 12,
                "business_monthly_equiv": income.business_income_annual / 12,
                "rental": income.rental_income_monthly,
                "other_monthly_equiv": income.other_income_annual / 12,
            },
        }

    def ratios(
        self,
        income: Income,
        expenses: Expenses,
        total_emi: float,
        total_sip: float,
        net_worth_value: float,
    ) -> dict[str, Any]:
        monthly_income = income.total_monthly_income or 1.0
        annual_income = income.total_annual_income or 1.0

        savings_rate = (monthly_income - expenses.total_monthly - total_emi) / monthly_income
        # Savings ratio including investments
        investment_rate = total_sip / monthly_income
        dti = total_emi / monthly_income
        expense_ratio = expenses.total_monthly / monthly_income
        net_worth_to_income = net_worth_value / annual_income

        return {
            "savings_ratio": round(savings_rate, 4),
            "savings_ratio_percent": round(savings_rate * 100, 2),
            "investment_rate": round(investment_rate, 4),
            "investment_rate_percent": round(investment_rate * 100, 2),
            "debt_to_income_ratio": round(dti, 4),
            "debt_to_income_percent": round(dti * 100, 2),
            "expense_ratio": round(expense_ratio, 4),
            "expense_ratio_percent": round(expense_ratio * 100, 2),
            "net_worth_to_annual_income": round(net_worth_to_income, 2),
            "benchmarks": {
                "savings_ratio_target": 0.20,
                "dti_max_comfortable": 0.40,
                "dti_max_aggressive": 0.50,
                "expense_ratio_target": 0.50,
            },
            "flags": {
                "low_savings": savings_rate < 0.20,
                "high_dti": dti > 0.40,
                "high_expenses": expense_ratio > 0.60,
            },
        }

    def emergency_fund(
        self,
        monthly_expenses: float,
        total_emi: float,
        current_emergency_fund: float,
        risk_profile: RiskProfile,
    ) -> dict[str, Any]:
        months_map = {
            RiskProfile.CONSERVATIVE: int(self.ef_cfg.get("conservative_months", 12)),
            RiskProfile.MODERATE: int(self.ef_cfg.get("moderate_months", 6)),
            RiskProfile.AGGRESSIVE: int(self.ef_cfg.get("aggressive_months", 3)),
        }
        months = months_map.get(risk_profile, 6)
        monthly_essential = monthly_expenses + total_emi
        required = monthly_essential * months
        gap = max(required - current_emergency_fund, 0.0)
        surplus = max(current_emergency_fund - required, 0.0)
        coverage_months = (
            current_emergency_fund / monthly_essential if monthly_essential > 0 else 0
        )

        return {
            "monthly_essential_expenses": round(monthly_essential, 2),
            "recommended_months": months,
            "required_amount": round(required, 2),
            "current_amount": round(current_emergency_fund, 2),
            "gap": round(gap, 2),
            "surplus": round(surplus, 2),
            "coverage_months": round(coverage_months, 2),
            "adequate": gap <= 0,
            "recommendation": (
                "Emergency fund is adequate."
                if gap <= 0
                else f"Build an additional ₹{gap:,.0f} in liquid instruments (savings / liquid funds)."
            ),
        }
