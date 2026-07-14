"""Typed data models for the financial planning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class MaritalStatus(str, Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class RiskProfile(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TaxRegime(str, Enum):
    OLD = "old"
    NEW = "new"


class GoalType(str, Enum):
    HOUSE = "house"
    CAR = "car"
    CHILDREN_EDUCATION = "children_education"
    CHILDREN_MARRIAGE = "children_marriage"
    RETIREMENT = "retirement"
    VACATION = "vacation"
    EMERGENCY = "emergency"
    BUSINESS = "business"
    CUSTOM = "custom"


class LoanType(str, Enum):
    HOME = "home"
    CAR = "car"
    PERSONAL = "personal"
    EDUCATION = "education"
    GOLD = "gold"
    CREDIT_CARD = "credit_card"
    OTHER = "other"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PersonalDetails:
    full_name: str = ""
    age: int = 30
    retirement_age: int = 60
    life_expectancy: int = 85
    marital_status: MaritalStatus = MaritalStatus.SINGLE
    dependents: int = 0
    children: int = 0
    city_type: str = "metro"  # metro | non_metro
    email: str = ""
    phone: str = ""
    pan: str = ""
    residential_status: str = "resident"


@dataclass
class Income:
    salary_monthly: float = 0.0
    bonus_annual: float = 0.0
    business_income_annual: float = 0.0
    rental_income_monthly: float = 0.0
    other_income_annual: float = 0.0
    employer_epf_contribution_monthly: float = 0.0
    employee_epf_contribution_monthly: float = 0.0

    @property
    def annual_salary(self) -> float:
        return self.salary_monthly * 12

    @property
    def annual_rental(self) -> float:
        return self.rental_income_monthly * 12

    @property
    def total_annual_income(self) -> float:
        return (
            self.annual_salary
            + self.bonus_annual
            + self.business_income_annual
            + self.annual_rental
            + self.other_income_annual
        )

    @property
    def total_monthly_income(self) -> float:
        return self.total_annual_income / 12


@dataclass
class Expenses:
    monthly_living: float = 0.0
    travel_monthly: float = 0.0
    medical_monthly: float = 0.0
    education_monthly: float = 0.0
    insurance_premium_monthly: float = 0.0
    entertainment_monthly: float = 0.0
    miscellaneous_monthly: float = 0.0
    rent_monthly: float = 0.0

    @property
    def total_monthly(self) -> float:
        return (
            self.monthly_living
            + self.travel_monthly
            + self.medical_monthly
            + self.education_monthly
            + self.insurance_premium_monthly
            + self.entertainment_monthly
            + self.miscellaneous_monthly
            + self.rent_monthly
        )

    @property
    def total_annual(self) -> float:
        return self.total_monthly * 12


@dataclass
class Loan:
    name: str
    loan_type: LoanType
    principal_outstanding: float
    interest_rate_annual: float
    emi: float
    tenure_months_remaining: int
    original_principal: float = 0.0
    prepayment_amount: float = 0.0
    start_date: Optional[str] = None


@dataclass
class Assets:
    savings: float = 0.0
    fd: float = 0.0
    ppf: float = 0.0
    epf: float = 0.0
    nps: float = 0.0
    mutual_funds: float = 0.0
    stocks: float = 0.0
    gold: float = 0.0
    real_estate: float = 0.0
    cash: float = 0.0
    emergency_fund: float = 0.0
    other: float = 0.0
    reit: float = 0.0
    invit: float = 0.0

    @property
    def liquid_assets(self) -> float:
        return self.savings + self.cash + self.emergency_fund + self.fd * 0.5

    @property
    def financial_assets(self) -> float:
        return (
            self.savings
            + self.fd
            + self.ppf
            + self.epf
            + self.nps
            + self.mutual_funds
            + self.stocks
            + self.gold
            + self.cash
            + self.emergency_fund
            + self.other
            + self.reit
            + self.invit
        )

    @property
    def total_assets(self) -> float:
        return self.financial_assets + self.real_estate


@dataclass
class Insurance:
    health_cover: float = 0.0
    health_premium_annual: float = 0.0
    life_cover: float = 0.0
    life_premium_annual: float = 0.0
    accident_cover: float = 0.0
    accident_premium_annual: float = 0.0
    critical_illness_cover: float = 0.0
    critical_illness_premium_annual: float = 0.0


@dataclass
class Investment:
    name: str
    category: str
    amount: float
    monthly_sip: float = 0.0
    expected_return: float = 0.12
    start_date: Optional[str] = None
    is_lumpsum: bool = False


@dataclass
class Goal:
    name: str
    goal_type: GoalType
    current_cost: float
    target_year: int
    priority: Priority = Priority.MEDIUM
    already_saved: float = 0.0
    inflation_rate: Optional[float] = None
    expected_return: Optional[float] = None
    notes: str = ""


@dataclass
class TaxInputs:
    regime_preference: TaxRegime = TaxRegime.NEW
    hra_received_annual: float = 0.0
    rent_paid_annual: float = 0.0
    section_80c_investments: float = 0.0
    section_80ccd_1b: float = 0.0
    section_80d_self: float = 0.0
    section_80d_parents: float = 0.0
    home_loan_interest: float = 0.0
    is_senior_citizen: bool = False
    parents_senior_citizen: bool = False
    ltcg_equity: float = 0.0
    stcg_equity: float = 0.0
    other_deductions: float = 0.0


@dataclass
class AssumptionsOverride:
    general_inflation: Optional[float] = None
    healthcare_inflation: Optional[float] = None
    education_inflation: Optional[float] = None
    expected_equity_return: Optional[float] = None
    expected_debt_return: Optional[float] = None
    safe_withdrawal_rate: Optional[float] = None
    salary_growth_rate: Optional[float] = None


@dataclass
class ClientFinancialProfile:
    """Complete configurable client financial profile — no hardcoded values."""

    personal: PersonalDetails = field(default_factory=PersonalDetails)
    income: Income = field(default_factory=Income)
    expenses: Expenses = field(default_factory=Expenses)
    loans: list[Loan] = field(default_factory=list)
    assets: Assets = field(default_factory=Assets)
    insurance: Insurance = field(default_factory=Insurance)
    investments: list[Investment] = field(default_factory=list)
    goals: list[Goal] = field(default_factory=list)
    tax: TaxInputs = field(default_factory=TaxInputs)
    risk_profile: RiskProfile = RiskProfile.MODERATE
    risk_answers: dict[str, str] = field(default_factory=dict)
    assumptions: AssumptionsOverride = field(default_factory=AssumptionsOverride)
    client_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClientFinancialProfile:
        """Build profile from a plain dictionary (API / form payload)."""
        personal_data = data.get("personal", {})
        income_data = data.get("income", {})
        expenses_data = data.get("expenses", {})
        assets_data = data.get("assets", {})
        insurance_data = data.get("insurance", {})
        tax_data = data.get("tax", {})
        assumptions_data = data.get("assumptions", {})

        personal = PersonalDetails(
            full_name=personal_data.get("full_name", ""),
            age=int(personal_data.get("age", 30)),
            retirement_age=int(personal_data.get("retirement_age", 60)),
            life_expectancy=int(personal_data.get("life_expectancy", 85)),
            marital_status=MaritalStatus(personal_data.get("marital_status", "single")),
            dependents=int(personal_data.get("dependents", 0)),
            children=int(personal_data.get("children", 0)),
            city_type=personal_data.get("city_type", "metro"),
            email=personal_data.get("email", ""),
            phone=personal_data.get("phone", ""),
            pan=personal_data.get("pan", ""),
            residential_status=personal_data.get("residential_status", "resident"),
        )

        income = Income(**{k: float(v) for k, v in income_data.items() if k in Income.__dataclass_fields__})
        expenses = Expenses(**{k: float(v) for k, v in expenses_data.items() if k in Expenses.__dataclass_fields__})
        assets = Assets(**{k: float(v) for k, v in assets_data.items() if k in Assets.__dataclass_fields__})
        insurance = Insurance(
            **{k: float(v) for k, v in insurance_data.items() if k in Insurance.__dataclass_fields__}
        )

        loans = [
            Loan(
                name=l.get("name", "Loan"),
                loan_type=LoanType(l.get("loan_type", "other")),
                principal_outstanding=float(l.get("principal_outstanding", 0)),
                interest_rate_annual=float(l.get("interest_rate_annual", 0)),
                emi=float(l.get("emi", 0)),
                tenure_months_remaining=int(l.get("tenure_months_remaining", 0)),
                original_principal=float(l.get("original_principal", 0)),
                prepayment_amount=float(l.get("prepayment_amount", 0)),
                start_date=l.get("start_date"),
            )
            for l in data.get("loans", [])
        ]

        investments = [
            Investment(
                name=i.get("name", "Investment"),
                category=i.get("category", "mutual_funds"),
                amount=float(i.get("amount", 0)),
                monthly_sip=float(i.get("monthly_sip", 0)),
                expected_return=float(i.get("expected_return", 0.12)),
                start_date=i.get("start_date"),
                is_lumpsum=bool(i.get("is_lumpsum", False)),
            )
            for i in data.get("investments", [])
        ]

        goals = [
            Goal(
                name=g.get("name", "Goal"),
                goal_type=GoalType(g.get("goal_type", "custom")),
                current_cost=float(g.get("current_cost", 0)),
                target_year=int(g.get("target_year", personal.age + 5)),
                priority=Priority(g.get("priority", "medium")),
                already_saved=float(g.get("already_saved", 0)),
                inflation_rate=g.get("inflation_rate"),
                expected_return=g.get("expected_return"),
                notes=g.get("notes", ""),
            )
            for g in data.get("goals", [])
        ]

        tax = TaxInputs(
            regime_preference=TaxRegime(tax_data.get("regime_preference", "new")),
            hra_received_annual=float(tax_data.get("hra_received_annual", 0)),
            rent_paid_annual=float(tax_data.get("rent_paid_annual", 0)),
            section_80c_investments=float(tax_data.get("section_80c_investments", 0)),
            section_80ccd_1b=float(tax_data.get("section_80ccd_1b", 0)),
            section_80d_self=float(tax_data.get("section_80d_self", 0)),
            section_80d_parents=float(tax_data.get("section_80d_parents", 0)),
            home_loan_interest=float(tax_data.get("home_loan_interest", 0)),
            is_senior_citizen=bool(tax_data.get("is_senior_citizen", False)),
            parents_senior_citizen=bool(tax_data.get("parents_senior_citizen", False)),
            ltcg_equity=float(tax_data.get("ltcg_equity", 0)),
            stcg_equity=float(tax_data.get("stcg_equity", 0)),
            other_deductions=float(tax_data.get("other_deductions", 0)),
        )

        assumptions = AssumptionsOverride(
            **{
                k: float(v) if v is not None else None
                for k, v in assumptions_data.items()
                if k in AssumptionsOverride.__dataclass_fields__
            }
        )

        risk_raw = data.get("risk_profile", "moderate")
        risk_profile = RiskProfile(risk_raw) if risk_raw in RiskProfile._value2member_map_ else RiskProfile.MODERATE

        return cls(
            personal=personal,
            income=income,
            expenses=expenses,
            loans=loans,
            assets=assets,
            insurance=insurance,
            investments=investments,
            goals=goals,
            tax=tax,
            risk_profile=risk_profile,
            risk_answers=data.get("risk_answers", {}),
            assumptions=assumptions,
            client_id=data.get("client_id"),
        )


@dataclass
class PlanResult:
    """Complete financial plan output."""

    net_worth: dict[str, Any]
    cash_flow: dict[str, Any]
    ratios: dict[str, Any]
    emergency_fund: dict[str, Any]
    goals: list[dict[str, Any]]
    retirement: dict[str, Any]
    loans: list[dict[str, Any]]
    tax: dict[str, Any]
    insurance: dict[str, Any]
    risk: dict[str, Any]
    recommendations: dict[str, Any]
    portfolio: dict[str, Any]
    health_score: dict[str, Any]
    scenarios: dict[str, Any]
    estate_checklist: list[dict[str, Any]]
    fire: dict[str, Any]
    assumptions_used: dict[str, Any]
    summary: dict[str, Any]
