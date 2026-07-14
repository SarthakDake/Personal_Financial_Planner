"""
Professional Financial Planning Engine.

Industry-grade calculations for Indian financial planning standards.
All formulas use real mathematical models — no mocks or placeholders.
"""

from financial_engine.engine import FinancialPlanningEngine
from financial_engine.models import ClientFinancialProfile, PlanResult

__all__ = [
    "FinancialPlanningEngine",
    "ClientFinancialProfile",
    "PlanResult",
]

__version__ = "1.0.0"
