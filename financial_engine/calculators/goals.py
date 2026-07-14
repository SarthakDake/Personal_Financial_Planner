"""Goal-based financial planning calculations."""

from __future__ import annotations

from typing import Any

from financial_engine.calculators.time_value import TimeValueCalculator
from financial_engine.models import Goal, GoalType


class GoalCalculator:
    """Unlimited goal planner with inflation-adjusted SIP/lumpsum requirements."""

    DEFAULT_INFLATION = {
        GoalType.HOUSE: 0.05,
        GoalType.CAR: 0.05,
        GoalType.CHILDREN_EDUCATION: 0.08,
        GoalType.CHILDREN_MARRIAGE: 0.07,
        GoalType.RETIREMENT: 0.06,
        GoalType.VACATION: 0.06,
        GoalType.EMERGENCY: 0.06,
        GoalType.BUSINESS: 0.06,
        GoalType.CUSTOM: 0.06,
    }

    def __init__(self, assumptions: dict[str, Any]):
        self.assumptions = assumptions
        inflation = assumptions.get("inflation", {})
        self.DEFAULT_INFLATION[GoalType.CHILDREN_EDUCATION] = float(
            inflation.get("education", 0.08)
        )
        self.DEFAULT_INFLATION[GoalType.RETIREMENT] = float(inflation.get("general", 0.06))
        self.DEFAULT_INFLATION[GoalType.HOUSE] = float(inflation.get("real_estate", 0.05))

    def plan_goal(
        self,
        goal: Goal,
        current_age: int,
        default_return: float = 0.12,
    ) -> dict[str, Any]:
        # Convention for target_year:
        #   > 1900  → calendar year
        #   100–1900 → client's age at goal
        #   < 100   → years from now (investment horizon)
        if goal.target_year > 1900:
            from datetime import datetime

            years = max(goal.target_year - datetime.now().year, 0)
        elif goal.target_year >= 100:
            years = max(goal.target_year - current_age, 0)
        else:
            years = max(int(goal.target_year), 0)

        inflation = (
            float(goal.inflation_rate)
            if goal.inflation_rate is not None
            else self.DEFAULT_INFLATION.get(goal.goal_type, 0.06)
        )
        expected_return = (
            float(goal.expected_return) if goal.expected_return is not None else default_return
        )

        future_cost = TimeValueCalculator.inflation_adjusted_value(
            goal.current_cost, inflation, years
        )
        monthly_sip = TimeValueCalculator.sip_required_for_goal(
            future_cost, expected_return, years, goal.already_saved
        )
        annual_sip = monthly_sip * 12
        lumpsum_required = TimeValueCalculator.lumpsum_required(
            future_cost, expected_return, years
        )
        # Adjust lumpsum for already saved
        fv_saved = TimeValueCalculator.future_value(goal.already_saved, expected_return, years)
        lumpsum_shortfall_pv = TimeValueCalculator.present_value(
            max(future_cost - fv_saved, 0.0), expected_return, years
        )

        progress = 0.0
        if future_cost > 0:
            progress = min(fv_saved / future_cost, 1.0) if years > 0 else min(
                goal.already_saved / goal.current_cost, 1.0
            ) if goal.current_cost > 0 else 0.0

        return {
            "name": goal.name,
            "goal_type": goal.goal_type.value,
            "priority": goal.priority.value,
            "current_cost": round(goal.current_cost, 2),
            "inflation_rate": inflation,
            "years_to_goal": years,
            "future_cost": round(future_cost, 2),
            "already_saved": round(goal.already_saved, 2),
            "expected_return": expected_return,
            "monthly_sip_required": round(monthly_sip, 2),
            "annual_sip_required": round(annual_sip, 2),
            "lumpsum_required": round(lumpsum_shortfall_pv, 2),
            "lumpsum_if_starting_fresh": round(lumpsum_required, 2),
            "projected_saved_corpus": round(fv_saved, 2),
            "funding_gap": round(max(future_cost - fv_saved, 0.0), 2),
            "progress_percent": round(progress * 100, 2),
            "notes": goal.notes,
        }

    def plan_all_goals(
        self,
        goals: list[Goal],
        current_age: int,
        risk_profile: str = "moderate",
    ) -> list[dict[str, Any]]:
        returns = self.assumptions.get("returns", {})
        profile_returns = {
            "conservative": float(returns.get("debt", 0.07)) * 0.4
            + float(returns.get("equity_large_cap", 0.12)) * 0.6,
            "moderate": float(returns.get("equity_flexi_cap", 0.13)),
            "aggressive": float(returns.get("equity_mid_cap", 0.14)),
        }
        default_return = profile_returns.get(risk_profile, 0.12)
        results = [self.plan_goal(g, current_age, default_return) for g in goals]
        priority_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["years_to_goal"]))
        return results
