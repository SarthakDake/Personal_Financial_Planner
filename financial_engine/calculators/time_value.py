"""Time value of money calculations — FV, PV, SIP, CAGR, XIRR, real returns."""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable, Sequence

import numpy as np
import numpy_financial as npf


class TimeValueCalculator:
    """Industry-standard TVM formulas used in wealth management."""

    @staticmethod
    def future_value(present_value: float, rate: float, periods: int) -> float:
        """FV = PV * (1 + r)^n"""
        if periods <= 0:
            return present_value
        return present_value * ((1 + rate) ** periods)

    @staticmethod
    def present_value(future_value: float, rate: float, periods: int) -> float:
        """PV = FV / (1 + r)^n"""
        if periods <= 0:
            return future_value
        return future_value / ((1 + rate) ** periods)

    @staticmethod
    def real_return(nominal_return: float, inflation: float) -> float:
        """Fisher equation: real = (1 + nominal) / (1 + inflation) - 1"""
        return ((1 + nominal_return) / (1 + inflation)) - 1

    @staticmethod
    def inflation_adjusted_value(current_value: float, inflation: float, years: int) -> float:
        """Future cost after inflation."""
        return TimeValueCalculator.future_value(current_value, inflation, years)

    @staticmethod
    def sip_future_value(monthly_investment: float, annual_rate: float, years: float) -> float:
        """
        Future value of a monthly SIP (ordinary annuity, end of period).

        FV = P * [((1 + r)^n - 1) / r] * (1 + r)
        where r = monthly rate, n = months
        """
        if monthly_investment <= 0 or years <= 0:
            return 0.0
        monthly_rate = annual_rate / 12
        months = int(round(years * 12))
        if monthly_rate == 0:
            return monthly_investment * months
        factor = (((1 + monthly_rate) ** months) - 1) / monthly_rate
        return monthly_investment * factor * (1 + monthly_rate)

    @staticmethod
    def sip_required_for_goal(
        target_amount: float,
        annual_rate: float,
        years: float,
        existing_corpus: float = 0.0,
    ) -> float:
        """Monthly SIP required to reach a future goal amount."""
        if years <= 0:
            gap = max(target_amount - existing_corpus, 0.0)
            return gap
        monthly_rate = annual_rate / 12
        months = max(int(round(years * 12)), 1)
        fv_existing = TimeValueCalculator.future_value(existing_corpus, annual_rate, int(years))
        remaining = max(target_amount - fv_existing, 0.0)
        if remaining <= 0:
            return 0.0
        if monthly_rate == 0:
            return remaining / months
        factor = (((1 + monthly_rate) ** months) - 1) / monthly_rate * (1 + monthly_rate)
        return remaining / factor

    @staticmethod
    def lumpsum_required(target_amount: float, annual_rate: float, years: float) -> float:
        """Present lumpsum required to grow to target."""
        return TimeValueCalculator.present_value(target_amount, annual_rate, int(max(years, 0)))

    @staticmethod
    def cagr(beginning_value: float, ending_value: float, years: float) -> float:
        """Compound Annual Growth Rate."""
        if beginning_value <= 0 or years <= 0:
            return 0.0
        return (ending_value / beginning_value) ** (1 / years) - 1

    @staticmethod
    def xirr(
        cash_flows: Sequence[float],
        dates: Sequence[date | datetime | str],
        guess: float = 0.1,
    ) -> float:
        """
        Extended Internal Rate of Return for irregular cash flows.

        cash_flows: negative for investments, positive for redemptions
        """
        if len(cash_flows) != len(dates) or len(cash_flows) < 2:
            return 0.0

        parsed_dates: list[date] = []
        for d in dates:
            if isinstance(d, datetime):
                parsed_dates.append(d.date())
            elif isinstance(d, date):
                parsed_dates.append(d)
            else:
                parsed_dates.append(datetime.fromisoformat(str(d)).date())

        base = parsed_dates[0]
        years = np.array([(d - base).days / 365.25 for d in parsed_dates], dtype=float)
        amounts = np.array(cash_flows, dtype=float)

        def npv(rate: float) -> float:
            return float(np.sum(amounts / ((1 + rate) ** years)))

        try:
            # Newton-Raphson
            rate = guess
            for _ in range(100):
                f = npv(rate)
                # derivative
                df = float(np.sum(-years * amounts / ((1 + rate) ** (years + 1))))
                if abs(df) < 1e-12:
                    break
                new_rate = rate - f / df
                if abs(new_rate - rate) < 1e-7:
                    return float(new_rate)
                rate = new_rate
            return float(rate)
        except Exception:
            try:
                return float(npf.irr(amounts))
            except Exception:
                return 0.0

    @staticmethod
    def annuity_payment(principal: float, annual_rate: float, years: float) -> float:
        """PMT for an ordinary annuity (annual)."""
        if years <= 0:
            return principal
        if annual_rate == 0:
            return principal / years
        return principal * (annual_rate * (1 + annual_rate) ** years) / (((1 + annual_rate) ** years) - 1)

    @staticmethod
    def growing_annuity_present_value(
        first_payment: float,
        discount_rate: float,
        growth_rate: float,
        periods: int,
    ) -> float:
        """PV of a growing annuity (Gordon-style for finite periods)."""
        if periods <= 0:
            return 0.0
        if abs(discount_rate - growth_rate) < 1e-12:
            return first_payment * periods / (1 + discount_rate)
        ratio = (1 + growth_rate) / (1 + discount_rate)
        return first_payment * (1 - (ratio ** periods)) / (discount_rate - growth_rate)

    @staticmethod
    def corpus_from_withdrawal(
        annual_withdrawal: float,
        safe_withdrawal_rate: float,
    ) -> float:
        """FIRE / corpus required = annual expenses / SWR."""
        if safe_withdrawal_rate <= 0:
            return float("inf")
        return annual_withdrawal / safe_withdrawal_rate
