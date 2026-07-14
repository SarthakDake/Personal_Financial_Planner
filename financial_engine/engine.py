"""
Orchestrates the complete financial plan generation pipeline.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from financial_engine.calculators.goals import GoalCalculator
from financial_engine.calculators.health_score import HealthScoreCalculator
from financial_engine.calculators.insurance import InsuranceCalculator
from financial_engine.calculators.loans import LoanCalculator
from financial_engine.calculators.monte_carlo import MonteCarloSimulator
from financial_engine.calculators.portfolio import PortfolioCalculator
from financial_engine.calculators.ratios import RatioCalculator
from financial_engine.calculators.retirement import RetirementCalculator
from financial_engine.calculators.tax import TaxCalculator
from financial_engine.calculators.time_value import TimeValueCalculator
from financial_engine.estate import generate_estate_checklist
from financial_engine.models import ClientFinancialProfile, PlanResult, RiskProfile
from financial_engine.risk_profiler import RiskProfiler
from financial_engine.scenarios import ScenarioAnalyzer, WhatIfAnalyzer

logger = logging.getLogger(__name__)


class FinancialPlanningEngine:
    """
    Production financial planning engine.

    Loads configurable assumptions and produces a complete PlanResult
    for any client profile — no hardcoded personal data.
    """

    def __init__(
        self,
        config_dir: str | Path = "config",
        assumptions_file: str = "assumptions.json",
        recommendations_file: str = "investment_recommendations.json",
        questionnaire_file: str = "risk_questionnaire.json",
    ):
        self.config_dir = Path(config_dir)
        with open(self.config_dir / assumptions_file, encoding="utf-8") as f:
            self.assumptions = json.load(f)

        self.recommendations_path = self.config_dir / recommendations_file
        self.risk_profiler = RiskProfiler(self.config_dir / questionnaire_file)

        self.ratio_calc = RatioCalculator(self.assumptions)
        self.goal_calc = GoalCalculator(self.assumptions)
        self.retirement_calc = RetirementCalculator(self.assumptions)
        self.tax_calc = TaxCalculator(self.assumptions.get("tax", {}))
        self.insurance_calc = InsuranceCalculator(self.assumptions)
        self.portfolio_calc = PortfolioCalculator(self.assumptions, self.recommendations_path)
        self.monte_carlo = MonteCarloSimulator(self.assumptions)
        self.health_calc = HealthScoreCalculator()
        self.scenario_analyzer = ScenarioAnalyzer(self.assumptions)

    def _merge_assumptions(self, profile: ClientFinancialProfile) -> dict[str, Any]:
        merged = json.loads(json.dumps(self.assumptions))  # deep copy
        ov = profile.assumptions
        if ov.general_inflation is not None:
            merged["inflation"]["general"] = ov.general_inflation
        if ov.healthcare_inflation is not None:
            merged["inflation"]["healthcare"] = ov.healthcare_inflation
        if ov.education_inflation is not None:
            merged["inflation"]["education"] = ov.education_inflation
        if ov.expected_equity_return is not None:
            merged["returns"]["equity_flexi_cap"] = ov.expected_equity_return
            merged["returns"]["equity_large_cap"] = ov.expected_equity_return * 0.95
        if ov.expected_debt_return is not None:
            merged["returns"]["debt"] = ov.expected_debt_return
        if ov.safe_withdrawal_rate is not None:
            merged["retirement"]["safe_withdrawal_rate"] = ov.safe_withdrawal_rate
        return merged

    def generate_plan(self, profile: ClientFinancialProfile) -> PlanResult:
        """Generate a complete financial plan for the given client profile."""
        logger.info(
            "Generating plan for client_id=%s age=%s",
            profile.client_id,
            profile.personal.age,
        )

        assumptions = self._merge_assumptions(profile)
        # Rebuild calculators with merged assumptions for this run
        ratio_calc = RatioCalculator(assumptions)
        goal_calc = GoalCalculator(assumptions)
        retirement_calc = RetirementCalculator(assumptions)
        tax_calc = TaxCalculator(assumptions.get("tax", {}))
        insurance_calc = InsuranceCalculator(assumptions)
        portfolio_calc = PortfolioCalculator(assumptions, self.recommendations_path)
        monte_carlo = MonteCarloSimulator(assumptions)

        # Risk profile from questionnaire if answers provided
        risk_result: dict[str, Any]
        if profile.risk_answers:
            risk_result = self.risk_profiler.score(profile.risk_answers)
            profile.risk_profile = RiskProfile(risk_result["profile"])
        else:
            risk_result = {
                "total_score": None,
                "profile": profile.risk_profile.value,
                "personality": profile.risk_profile.value.title(),
                "description": "Risk profile provided directly without questionnaire.",
                "answers_detail": [],
            }

        # Loans
        loan_analyses = [
            LoanCalculator.analyze_loan(
                name=loan.name,
                loan_type=loan.loan_type.value,
                principal_outstanding=loan.principal_outstanding,
                annual_rate=loan.interest_rate_annual,
                emi=loan.emi
                or LoanCalculator.calculate_emi(
                    loan.principal_outstanding,
                    loan.interest_rate_annual,
                    max(loan.tenure_months_remaining, 1),
                ),
                tenure_months=max(loan.tenure_months_remaining, 1),
                prepayment=loan.prepayment_amount,
            )
            for loan in profile.loans
        ]
        total_emi = sum(l["emi"] for l in loan_analyses)
        total_liabilities = sum(l["principal_outstanding"] for l in loan_analyses)

        total_sip = sum(i.monthly_sip for i in profile.investments)

        # Net worth & cash flow
        net_worth = ratio_calc.net_worth(profile.assets, total_liabilities)
        cash_flow = ratio_calc.cash_flow(profile.income, profile.expenses, total_emi, total_sip)
        ratios = ratio_calc.ratios(
            profile.income,
            profile.expenses,
            total_emi,
            total_sip,
            net_worth["net_worth"],
        )
        emergency = ratio_calc.emergency_fund(
            profile.expenses.total_monthly,
            total_emi,
            profile.assets.emergency_fund + profile.assets.liquid_assets * 0.5,
            profile.risk_profile,
        )

        # Goals
        goals = goal_calc.plan_all_goals(
            profile.goals, profile.personal.age, profile.risk_profile.value
        )
        goals_avg_progress = (
            sum(g["progress_percent"] for g in goals) / len(goals) if goals else 50.0
        )
        goals_funding_gap = sum(g["funding_gap"] for g in goals)

        # Retirement
        retirement = retirement_calc.calculate(
            current_age=profile.personal.age,
            retirement_age=profile.personal.retirement_age,
            life_expectancy=profile.personal.life_expectancy,
            current_annual_expenses=profile.expenses.total_annual,
            income=profile.income,
            assets=profile.assets,
            monthly_sip=total_sip,
            expected_return_pre=profile.assumptions.expected_equity_return,
            inflation=assumptions["inflation"]["general"],
            healthcare_inflation=assumptions["inflation"]["healthcare"],
            safe_withdrawal_rate=profile.assumptions.safe_withdrawal_rate,
        )

        # Monte Carlo on projected corpus
        mc = monte_carlo.simulate_retirement(
            initial_corpus=retirement["projected_corpus"],
            annual_withdrawal=retirement["net_annual_withdrawal_need"],
            years=retirement["years_in_retirement"],
            expected_return=retirement["expected_return_post_retirement"],
            inflation=assumptions["inflation"]["general"],
        )
        retirement["monte_carlo"] = mc

        # FIRE number
        fire_number = TimeValueCalculator.corpus_from_withdrawal(
            profile.expenses.total_annual,
            assumptions["retirement"]["safe_withdrawal_rate"],
        )
        fire = {
            "fire_number": round(fire_number, 2),
            "safe_withdrawal_rate": assumptions["retirement"]["safe_withdrawal_rate"],
            "current_progress_percent": round(
                min(profile.assets.financial_assets / fire_number * 100, 100), 2
            )
            if fire_number > 0
            else 0,
            "annual_expenses": round(profile.expenses.total_annual, 2),
            "gap": round(max(fire_number - profile.assets.financial_assets, 0), 2),
        }

        # Tax
        gross = profile.income.total_annual_income
        tax = tax_calc.compare_regimes(
            gross,
            basic_salary_annual=profile.income.annual_salary * 0.4,
            hra_received=profile.tax.hra_received_annual,
            rent_paid=profile.tax.rent_paid_annual or profile.expenses.rent_monthly * 12,
            is_metro=profile.personal.city_type == "metro",
            section_80c=profile.tax.section_80c_investments,
            section_80ccd_1b=profile.tax.section_80ccd_1b,
            section_80d_self=profile.tax.section_80d_self,
            section_80d_parents=profile.tax.section_80d_parents,
            home_loan_interest=profile.tax.home_loan_interest
            or sum(
                l["amortization"][0]["interest"] * 12
                if l["amortization"]
                else 0
                for l in loan_analyses
                if l["loan_type"] == "home"
            ),
            is_senior=profile.tax.is_senior_citizen or profile.personal.age >= 60,
            parents_senior=profile.tax.parents_senior_citizen,
            other_deductions=profile.tax.other_deductions,
            ltcg_equity=profile.tax.ltcg_equity,
            stcg_equity=profile.tax.stcg_equity,
        )
        preferred = profile.tax.regime_preference.value
        tax["client_preference"] = preferred
        tax["using_recommended"] = preferred == tax["recommended_regime"] or tax[
            "recommended_regime"
        ] == "either"

        # Insurance
        insurance = insurance_calc.analyze(
            personal=profile.personal,
            annual_income=gross,
            annual_expenses=profile.expenses.total_annual,
            outstanding_liabilities=total_liabilities,
            existing_insurance=profile.insurance,
            goals_funding_gap=goals_funding_gap,
        )

        # Portfolio & recommendations
        current_portfolio = portfolio_calc.current_allocation(profile.assets)
        reco = portfolio_calc.recommend(
            profile.risk_profile,
            profile.personal.age,
            cash_flow["investable_surplus"],
            goal_horizons=[g["years_to_goal"] for g in goals] or [10],
        )
        rebalance = portfolio_calc.rebalancing_needs(current_portfolio, reco["target_allocation"])
        portfolio = {
            "current": current_portfolio,
            "target": reco["target_allocation"],
            "rebalancing": rebalance,
            "investments": [
                {
                    "name": i.name,
                    "category": i.category,
                    "amount": i.amount,
                    "monthly_sip": i.monthly_sip,
                    "expected_return": i.expected_return,
                    "projected_1y": round(
                        TimeValueCalculator.future_value(i.amount, i.expected_return, 1)
                        + TimeValueCalculator.sip_future_value(i.monthly_sip, i.expected_return, 1),
                        2,
                    ),
                }
                for i in profile.investments
            ],
        }

        # Health score
        health = self.health_calc.calculate(
            savings_ratio=ratios["savings_ratio"],
            emergency_adequate=emergency["adequate"],
            emergency_coverage_months=emergency["coverage_months"],
            recommended_ef_months=emergency["recommended_months"],
            dti=ratios["debt_to_income_ratio"],
            life_adequate=insurance["life"]["adequate"],
            health_adequate=insurance["health"]["adequate"],
            retirement_progress=retirement["progress_percent"],
            goals_avg_progress=goals_avg_progress,
            equity_percent=current_portfolio.get("asset_class_percent", {}).get("equity", 0),
            debt_percent=current_portfolio.get("asset_class_percent", {}).get("debt", 0),
            recommended_regime_selected=tax["using_recommended"],
        )

        estate = generate_estate_checklist(profile)

        # Action plan recommendations (aggregated)
        recommendations = {
            "investment": reco,
            "priority_actions": self._priority_actions(
                emergency, insurance, retirement, goals, ratios, tax
            ),
            "asset_allocation": reco["target_allocation"],
            "rebalancing": rebalance,
        }

        summary = {
            "client_name": profile.personal.full_name,
            "age": profile.personal.age,
            "retirement_age": profile.personal.retirement_age,
            "risk_profile": profile.risk_profile.value,
            "net_worth": net_worth["net_worth"],
            "monthly_income": cash_flow["monthly_income"],
            "monthly_surplus": cash_flow["monthly_surplus"],
            "health_score": health["score"],
            "health_grade": health["grade"],
            "retirement_progress_percent": retirement["progress_percent"],
            "recommended_tax_regime": tax["recommended_regime"],
            "total_goals": len(goals),
            "total_loans": len(loan_analyses),
        }

        # Scenarios — avoid infinite recursion by computing lightweight variants
        scenarios = self._compute_scenarios(profile)

        return PlanResult(
            net_worth=net_worth,
            cash_flow=cash_flow,
            ratios=ratios,
            emergency_fund=emergency,
            goals=goals,
            retirement=retirement,
            loans=loan_analyses,
            tax=tax,
            insurance=insurance,
            risk=risk_result,
            recommendations=recommendations,
            portfolio=portfolio,
            health_score=health,
            scenarios=scenarios,
            estate_checklist=estate,
            fire=fire,
            assumptions_used={
                "inflation": assumptions["inflation"],
                "returns": assumptions["returns"],
                "retirement": assumptions["retirement"],
                "tax_year": assumptions.get("tax", {}).get("financial_year"),
            },
            summary=summary,
        )

    def _compute_scenarios(self, profile: ClientFinancialProfile) -> dict[str, Any]:
        """Run best/expected/worst without full recursive plan generation."""
        results = {}
        for name in ("best_case", "expected_case", "worst_case"):
            variant = self.scenario_analyzer.build_profile_variant(profile, name)
            # Partial plan focusing on retirement & cash flow
            assumptions = self._merge_assumptions(variant)
            ratio_calc = RatioCalculator(assumptions)
            retirement_calc = RetirementCalculator(assumptions)
            total_emi = sum(
                l.emi
                or LoanCalculator.calculate_emi(
                    l.principal_outstanding, l.interest_rate_annual, max(l.tenure_months_remaining, 1)
                )
                for l in variant.loans
            )
            total_sip = sum(i.monthly_sip for i in variant.investments)
            cf = ratio_calc.cash_flow(variant.income, variant.expenses, total_emi, total_sip)
            ret = retirement_calc.calculate(
                current_age=variant.personal.age,
                retirement_age=variant.personal.retirement_age,
                life_expectancy=variant.personal.life_expectancy,
                current_annual_expenses=variant.expenses.total_annual,
                income=variant.income,
                assets=variant.assets,
                monthly_sip=total_sip,
                expected_return_pre=variant.assumptions.expected_equity_return,
                inflation=assumptions["inflation"]["general"],
            )
            results[name] = {
                "label": name.replace("_", " ").title(),
                "assumptions": self.assumptions.get("scenarios", {}).get(name, {}),
                "monthly_surplus": cf["monthly_surplus"],
                "required_corpus": ret["required_corpus"],
                "projected_corpus": ret["projected_corpus"],
                "shortfall": ret["shortfall"],
                "progress_percent": ret["progress_percent"],
            }
        return results

    def what_if(self, profile: ClientFinancialProfile, adjustments: dict[str, Any]) -> PlanResult:
        """Apply what-if sliders and regenerate plan."""
        variant = WhatIfAnalyzer.apply_adjustments(
            profile,
            income_change_percent=float(adjustments.get("income_change_percent", 0)),
            expense_change_percent=float(adjustments.get("expense_change_percent", 0)),
            sip_change_absolute=float(adjustments.get("sip_change_absolute", 0)),
            inflation_override=adjustments.get("inflation_override"),
            returns_override=adjustments.get("returns_override"),
            loan_interest_change_percent=float(
                adjustments.get("loan_interest_change_percent", 0)
            ),
            retirement_age_override=adjustments.get("retirement_age_override"),
        )
        return self.generate_plan(variant)

    @staticmethod
    def _priority_actions(
        emergency: dict,
        insurance: dict,
        retirement: dict,
        goals: list,
        ratios: dict,
        tax: dict,
    ) -> list[dict[str, str]]:
        actions: list[dict[str, str]] = []
        if not emergency["adequate"]:
            actions.append(
                {
                    "priority": "1",
                    "area": "Emergency Fund",
                    "action": emergency["recommendation"],
                }
            )
        if not insurance["life"]["adequate"]:
            actions.append(
                {
                    "priority": "2",
                    "area": "Life Insurance",
                    "action": insurance["recommendations"][0]
                    if insurance["recommendations"]
                    else "Increase term cover.",
                }
            )
        if not insurance["health"]["adequate"]:
            actions.append(
                {
                    "priority": "3",
                    "area": "Health Insurance",
                    "action": next(
                        (r for r in insurance["recommendations"] if "health" in r.lower()),
                        "Enhance health cover.",
                    ),
                }
            )
        if ratios["flags"]["high_dti"]:
            actions.append(
                {
                    "priority": "4",
                    "area": "Debt",
                    "action": "Debt-to-income exceeds 40%. Prioritize prepayment of high-interest loans.",
                }
            )
        if retirement["shortfall"] > 0:
            actions.append(
                {
                    "priority": "5",
                    "area": "Retirement",
                    "action": (
                        f"Increase monthly retirement SIP by ₹{retirement['additional_monthly_sip_required']:,.0f} "
                        f"to close a corpus shortfall of ₹{retirement['shortfall']:,.0f}."
                    ),
                }
            )
        high_goals = [g for g in goals if g["priority"] == "high" and g["funding_gap"] > 0]
        for g in high_goals[:2]:
            actions.append(
                {
                    "priority": "6",
                    "area": f"Goal: {g['name']}",
                    "action": (
                        f"Start SIP of ₹{g['monthly_sip_required']:,.0f}/month to fund "
                        f"{g['name']} (future cost ₹{g['future_cost']:,.0f})."
                    ),
                }
            )
        if tax["recommended_regime"] not in ("either",):
            actions.append(
                {
                    "priority": "7",
                    "area": "Tax",
                    "action": tax["recommendation_text"],
                }
            )
        if ratios["flags"]["low_savings"]:
            actions.append(
                {
                    "priority": "8",
                    "area": "Savings",
                    "action": "Savings rate below 20%. Review discretionary expenses and automate investments.",
                }
            )
        return actions

    def plan_to_dict(self, plan: PlanResult) -> dict[str, Any]:
        """Serialize PlanResult to a JSON-safe dictionary."""
        return {
            "summary": plan.summary,
            "net_worth": plan.net_worth,
            "cash_flow": plan.cash_flow,
            "ratios": plan.ratios,
            "emergency_fund": plan.emergency_fund,
            "goals": plan.goals,
            "retirement": plan.retirement,
            "loans": [
                {k: v for k, v in loan.items() if k not in ("amortization", "amortization_with_prepayment")}
                | {
                    "amortization_preview": loan.get("amortization", [])[:12],
                    "amortization_months": len(loan.get("amortization", [])),
                }
                for loan in plan.loans
            ],
            "loans_full": plan.loans,
            "tax": plan.tax,
            "insurance": plan.insurance,
            "risk": plan.risk,
            "recommendations": plan.recommendations,
            "portfolio": plan.portfolio,
            "health_score": plan.health_score,
            "scenarios": plan.scenarios,
            "estate_checklist": plan.estate_checklist,
            "fire": plan.fire,
            "assumptions_used": plan.assumptions_used,
        }
