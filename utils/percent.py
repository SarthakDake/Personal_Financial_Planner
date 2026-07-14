"""Helpers for user-facing percentage inputs (5 = 5%) vs engine decimals (0.05)."""

from __future__ import annotations

from typing import Any, Optional


def percent_to_decimal(value: Optional[float | int]) -> Optional[float]:
    """Convert a human percentage to a decimal rate.

    Examples: 5 -> 0.05, 8.5 -> 0.085, 0 -> 0.0
    None stays None (caller may treat as 'use default').
    """
    if value is None:
        return None
    return float(value) / 100.0


def decimal_to_percent(value: Optional[float | int]) -> Optional[float]:
    """Convert a decimal rate to a human percentage."""
    if value is None:
        return None
    return round(float(value) * 100.0, 4)


def convert_profile_rates_to_decimal(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a deep-copied profile dict with rate fields converted from % → decimal.

    User-facing / stored profile JSON uses whole percentages (e.g. 8.5 for 8.5%).
    The financial engine expects decimal rates (0.085).
    """
    import copy

    out = copy.deepcopy(data)

    for loan in out.get("loans", []) or []:
        if "interest_rate_annual" in loan and loan["interest_rate_annual"] is not None:
            loan["interest_rate_annual"] = percent_to_decimal(loan["interest_rate_annual"])

    for inv in out.get("investments", []) or []:
        if "expected_return" in inv and inv["expected_return"] is not None:
            inv["expected_return"] = percent_to_decimal(inv["expected_return"])

    for goal in out.get("goals", []) or []:
        if goal.get("inflation_rate") is not None:
            goal["inflation_rate"] = percent_to_decimal(goal["inflation_rate"])
        if goal.get("expected_return") is not None:
            goal["expected_return"] = percent_to_decimal(goal["expected_return"])

    assumptions = out.get("assumptions") or {}
    rate_keys = (
        "general_inflation",
        "healthcare_inflation",
        "education_inflation",
        "expected_equity_return",
        "expected_debt_return",
        "safe_withdrawal_rate",
        "salary_growth_rate",
    )
    for key in rate_keys:
        if assumptions.get(key) is not None and assumptions.get(key) != "":
            # Treat 0 as "unset" for optional overrides (UI sends 0 when blank)
            if float(assumptions[key]) == 0:
                assumptions[key] = None
            else:
                assumptions[key] = percent_to_decimal(assumptions[key])
    out["assumptions"] = assumptions
    return out
