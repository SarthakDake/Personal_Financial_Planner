"""Portfolio allocation, asset mapping, and investment recommendations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from financial_engine.models import Assets, RiskProfile


class PortfolioCalculator:
    """Asset allocation analysis and configurable recommendation engine."""

    def __init__(self, assumptions: dict[str, Any], recommendations_path: str | Path):
        self.assumptions = assumptions
        self.risk_profiles = assumptions.get("risk_profiles", {})
        with open(recommendations_path, encoding="utf-8") as f:
            self.reco_config = json.load(f)

    def current_allocation(self, assets: Assets) -> dict[str, Any]:
        total = assets.total_assets
        if total <= 0:
            return {
                "total_assets": 0,
                "financial_assets": 0,
                "allocation": {},
                "allocation_percent": {},
            }

        allocation = {
            "cash_and_savings": assets.savings + assets.cash + assets.emergency_fund,
            "fixed_deposits": assets.fd,
            "ppf": assets.ppf,
            "epf": assets.epf,
            "nps": assets.nps,
            "mutual_funds": assets.mutual_funds,
            "stocks": assets.stocks,
            "gold": assets.gold,
            "real_estate": assets.real_estate,
            "reit": assets.reit,
            "invit": assets.invit,
            "other": assets.other,
        }
        percent = {k: round(v / total * 100, 2) for k, v in allocation.items()}

        equity = assets.mutual_funds * 0.7 + assets.stocks + assets.nps * 0.5
        debt = (
            assets.fd
            + assets.ppf
            + assets.epf
            + assets.nps * 0.5
            + assets.mutual_funds * 0.2
            + assets.savings
            + assets.cash
            + assets.emergency_fund
        )
        gold = assets.gold
        real_estate = assets.real_estate + assets.reit + assets.invit
        hybrid_other = assets.mutual_funds * 0.1 + assets.other

        asset_class = {
            "equity": round(equity, 2),
            "debt": round(debt, 2),
            "gold": round(gold, 2),
            "real_estate": round(real_estate, 2),
            "hybrid_other": round(hybrid_other, 2),
        }
        asset_class_pct = {
            k: round(v / total * 100, 2) for k, v in asset_class.items()
        }

        return {
            "total_assets": round(total, 2),
            "financial_assets": round(assets.financial_assets, 2),
            "allocation": {k: round(v, 2) for k, v in allocation.items()},
            "allocation_percent": percent,
            "asset_class": asset_class,
            "asset_class_percent": asset_class_pct,
        }

    def target_allocation(self, risk_profile: RiskProfile, age: int) -> dict[str, Any]:
        profile_key = risk_profile.value
        base = dict(self.risk_profiles.get(profile_key, self.risk_profiles.get("moderate", {})))

        # Age-based equity cap: 100 - age
        age_cfg = self.reco_config.get("age_based_equity_cap", {})
        max_equity = min(float(age_cfg.get("max_equity", 0.90)), (100 - age) / 100)
        min_equity = float(age_cfg.get("min_equity", 0.20))
        equity = max(min_equity, min(float(base.get("equity", 0.55)), max_equity))

        # Renormalize remaining
        others = {k: float(v) for k, v in base.items() if k != "equity"}
        other_sum = sum(others.values()) or 1.0
        scale = (1 - equity) / other_sum
        target = {"equity": round(equity, 4)}
        target.update({k: round(v * scale, 4) for k, v in others.items()})

        return {
            "risk_profile": profile_key,
            "age": age,
            "target_allocation": target,
            "age_adjusted_equity_cap": round(max_equity, 4),
        }

    def recommend(
        self,
        risk_profile: RiskProfile,
        age: int,
        investable_surplus_monthly: float,
        goal_horizons: list[int] | None = None,
    ) -> dict[str, Any]:
        profile = risk_profile.value
        target = self.target_allocation(risk_profile, age)
        asset_classes = self.reco_config.get("asset_classes", [])

        min_horizon = min(goal_horizons) if goal_horizons else 10
        recommendations: list[dict[str, Any]] = []

        for ac in asset_classes:
            rules = ac.get("allocation_rules", {}).get(profile, {})
            mid = (float(rules.get("min", 0)) + float(rules.get("max", 0))) / 2
            if mid <= 0 and profile not in ac.get("suitable_profiles", []):
                continue
            if ac.get("min_horizon_years", 0) > max(min_horizon, 5) and mid == 0:
                continue

            monthly_amount = investable_surplus_monthly * mid
            recommendations.append(
                {
                    "id": ac["id"],
                    "name": ac["name"],
                    "category": ac["category"],
                    "risk_level": ac["risk_level"],
                    "allocation_percent": round(mid * 100, 2),
                    "monthly_amount": round(monthly_amount, 2),
                    "annual_amount": round(monthly_amount * 12, 2),
                    "description": ac["description"],
                    "min_horizon_years": ac.get("min_horizon_years", 0),
                }
            )

        recommendations = [r for r in recommendations if r["allocation_percent"] > 0]
        # Normalize to 100%
        total_pct = sum(r["allocation_percent"] for r in recommendations) or 100
        for r in recommendations:
            r["allocation_percent"] = round(r["allocation_percent"] / total_pct * 100, 2)
            r["monthly_amount"] = round(
                investable_surplus_monthly * r["allocation_percent"] / 100, 2
            )
            r["annual_amount"] = round(r["monthly_amount"] * 12, 2)

        return {
            "target_allocation": target,
            "monthly_investable_surplus": round(investable_surplus_monthly, 2),
            "recommendations": recommendations,
            "disclaimer": (
                "Recommendations are category-level allocations based on risk profile, age, "
                "and horizon. Specific scheme selection should follow SEBI-registered advisor "
                "due diligence. No schemes are hardcoded."
            ),
        }

    def rebalancing_needs(
        self, current: dict[str, Any], target: dict[str, Any]
    ) -> list[dict[str, Any]]:
        current_ac = current.get("asset_class_percent", {})
        target_ac = {
            k: v * 100 for k, v in target.get("target_allocation", {}).items()
        }
        mapping = {
            "equity": current_ac.get("equity", 0),
            "debt": current_ac.get("debt", 0),
            "gold": current_ac.get("gold", 0),
            "hybrid": current_ac.get("hybrid_other", 0),
            "liquid": 0,
        }
        needs = []
        for key, tgt in target_ac.items():
            cur = mapping.get(key, 0)
            diff = tgt - cur
            if abs(diff) >= 2:  # 2% threshold
                needs.append(
                    {
                        "asset_class": key,
                        "current_percent": round(cur, 2),
                        "target_percent": round(tgt, 2),
                        "difference_percent": round(diff, 2),
                        "action": "increase" if diff > 0 else "decrease",
                    }
                )
        return needs
