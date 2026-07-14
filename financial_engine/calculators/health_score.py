"""Financial Health Score — composite 0-100 scorecard."""

from __future__ import annotations

from typing import Any


class HealthScoreCalculator:
    """
    Weighted financial health score used in advisory dashboards.

    Components (weights):
    - Savings rate (15)
    - Emergency fund (15)
    - Debt burden (15)
    - Insurance adequacy (15)
    - Retirement progress (15)
    - Goal funding (10)
    - Investment diversification (10)
    - Tax efficiency (5)
    """

    WEIGHTS = {
        "savings": 15,
        "emergency_fund": 15,
        "debt": 15,
        "insurance": 15,
        "retirement": 15,
        "goals": 10,
        "diversification": 10,
        "tax": 5,
    }

    def calculate(
        self,
        *,
        savings_ratio: float,
        emergency_adequate: bool,
        emergency_coverage_months: float,
        recommended_ef_months: float,
        dti: float,
        life_adequate: bool,
        health_adequate: bool,
        retirement_progress: float,
        goals_avg_progress: float,
        equity_percent: float,
        debt_percent: float,
        recommended_regime_selected: bool,
    ) -> dict[str, Any]:
        scores: dict[str, float] = {}

        # Savings: 20%+ = 100, 0% = 0
        scores["savings"] = min(max(savings_ratio / 0.20, 0), 1.5) * 100
        scores["savings"] = min(scores["savings"], 100)

        # Emergency fund
        if recommended_ef_months > 0:
            scores["emergency_fund"] = min(
                emergency_coverage_months / recommended_ef_months * 100, 100
            )
        else:
            scores["emergency_fund"] = 100 if emergency_adequate else 50

        # Debt: DTI 0 = 100, DTI 50%+ = 0
        scores["debt"] = max(0, (1 - dti / 0.50) * 100)

        # Insurance
        ins = 0
        if life_adequate:
            ins += 60
        if health_adequate:
            ins += 40
        scores["insurance"] = ins

        # Retirement progress
        scores["retirement"] = min(max(retirement_progress, 0), 100)

        # Goals
        scores["goals"] = min(max(goals_avg_progress, 0), 100)

        # Diversification: reward balanced allocation
        # Ideal: not 100% in one class
        concentration_penalty = max(equity_percent, debt_percent, 100 - equity_percent - debt_percent)
        scores["diversification"] = max(0, 100 - (concentration_penalty - 60) * 2) if concentration_penalty > 60 else 100

        # Tax
        scores["tax"] = 100 if recommended_regime_selected else 60

        weighted = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS) / sum(self.WEIGHTS.values())
        grade = self._grade(weighted)

        return {
            "score": round(weighted, 1),
            "grade": grade,
            "component_scores": {k: round(v, 1) for k, v in scores.items()},
            "weights": self.WEIGHTS,
            "interpretation": self._interpret(weighted),
            "top_improvements": self._improvements(scores),
        }

    @staticmethod
    def _grade(score: float) -> str:
        if score >= 85:
            return "A"
        if score >= 70:
            return "B"
        if score >= 55:
            return "C"
        if score >= 40:
            return "D"
        return "F"

    @staticmethod
    def _interpret(score: float) -> str:
        if score >= 85:
            return "Excellent financial health. Maintain discipline and review annually."
        if score >= 70:
            return "Good financial health with room for targeted improvements."
        if score >= 55:
            return "Average financial health. Priority actions needed in weaker areas."
        if score >= 40:
            return "Below-average financial health. Focus on emergency fund, debt, and savings."
        return "Critical. Immediate attention required on cash flow, protection, and debt."

    @staticmethod
    def _improvements(scores: dict[str, float]) -> list[str]:
        labels = {
            "savings": "Increase monthly savings rate toward 20%+",
            "emergency_fund": "Build liquid emergency reserves to recommended months",
            "debt": "Reduce EMI burden / accelerate high-interest loan prepayment",
            "insurance": "Close life and health insurance cover gaps",
            "retirement": "Increase retirement SIP to close corpus shortfall",
            "goals": "Fund high-priority goals with dedicated SIPs",
            "diversification": "Rebalance portfolio toward target asset allocation",
            "tax": "Adopt the tax regime that minimizes liability",
        }
        ranked = sorted(scores.items(), key=lambda x: x[1])
        return [labels[k] for k, _ in ranked[:3]]
