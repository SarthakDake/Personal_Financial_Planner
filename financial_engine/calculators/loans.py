"""Loan EMI, amortization, and prepayment analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd


class LoanCalculator:
    """EMI and amortization engine for Indian retail loans."""

    @staticmethod
    def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
        """
        Standard reducing-balance EMI formula.

        EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        where r = monthly interest rate
        """
        if principal <= 0 or tenure_months <= 0:
            return 0.0
        monthly_rate = annual_rate / 12
        if monthly_rate == 0:
            return principal / tenure_months
        factor = (1 + monthly_rate) ** tenure_months
        return principal * monthly_rate * factor / (factor - 1)

    @staticmethod
    def amortization_schedule(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        emi: float | None = None,
        prepayment: float = 0.0,
        prepayment_month: int = 1,
    ) -> pd.DataFrame:
        """Generate month-by-month amortization schedule with optional prepayment."""
        if principal <= 0 or tenure_months <= 0:
            return pd.DataFrame(
                columns=[
                    "month",
                    "opening_balance",
                    "emi",
                    "interest",
                    "principal",
                    "prepayment",
                    "closing_balance",
                    "cumulative_interest",
                ]
            )

        monthly_rate = annual_rate / 12
        if emi is None or emi <= 0:
            emi = LoanCalculator.calculate_emi(principal, annual_rate, tenure_months)

        rows: list[dict[str, Any]] = []
        balance = principal
        cumulative_interest = 0.0
        month = 0

        while balance > 0.01 and month < tenure_months + 120:
            month += 1
            opening = balance
            interest = opening * monthly_rate
            principal_component = min(emi - interest, opening)
            if principal_component < 0:
                principal_component = 0.0
            actual_emi = interest + principal_component
            prep = 0.0
            if month == prepayment_month and prepayment > 0:
                prep = min(prepayment, opening - principal_component)
            closing = max(opening - principal_component - prep, 0.0)
            cumulative_interest += interest
            rows.append(
                {
                    "month": month,
                    "opening_balance": round(opening, 2),
                    "emi": round(actual_emi, 2),
                    "interest": round(interest, 2),
                    "principal": round(principal_component, 2),
                    "prepayment": round(prep, 2),
                    "closing_balance": round(closing, 2),
                    "cumulative_interest": round(cumulative_interest, 2),
                }
            )
            balance = closing
            if balance <= 0.01:
                break

        return pd.DataFrame(rows)

    @staticmethod
    def analyze_loan(
        name: str,
        loan_type: str,
        principal_outstanding: float,
        annual_rate: float,
        emi: float,
        tenure_months: int,
        prepayment: float = 0.0,
    ) -> dict[str, Any]:
        """Full loan analysis including interest saved via prepayment."""
        base_schedule = LoanCalculator.amortization_schedule(
            principal_outstanding, annual_rate, tenure_months, emi
        )
        base_interest = float(base_schedule["interest"].sum()) if not base_schedule.empty else 0.0
        base_months = int(len(base_schedule))

        prep_schedule = LoanCalculator.amortization_schedule(
            principal_outstanding,
            annual_rate,
            tenure_months,
            emi,
            prepayment=prepayment,
            prepayment_month=1,
        )
        prep_interest = float(prep_schedule["interest"].sum()) if not prep_schedule.empty else 0.0
        prep_months = int(len(prep_schedule))

        return {
            "name": name,
            "loan_type": loan_type,
            "principal_outstanding": round(principal_outstanding, 2),
            "interest_rate_annual": annual_rate,
            "emi": round(emi, 2),
            "tenure_months_remaining": tenure_months,
            "total_interest_without_prepayment": round(base_interest, 2),
            "total_payable_without_prepayment": round(principal_outstanding + base_interest, 2),
            "closure_months_without_prepayment": base_months,
            "prepayment_amount": round(prepayment, 2),
            "total_interest_with_prepayment": round(prep_interest, 2),
            "interest_saved": round(max(base_interest - prep_interest, 0.0), 2),
            "months_saved": max(base_months - prep_months, 0),
            "closure_months_with_prepayment": prep_months,
            "amortization": base_schedule.to_dict(orient="records"),
            "amortization_with_prepayment": prep_schedule.to_dict(orient="records")
            if prepayment > 0
            else [],
        }

    @staticmethod
    def total_emi(loans: list[dict[str, Any]]) -> float:
        return sum(float(l.get("emi", 0)) for l in loans)

    @staticmethod
    def total_outstanding(loans: list[dict[str, Any]]) -> float:
        return sum(float(l.get("principal_outstanding", 0)) for l in loans)
