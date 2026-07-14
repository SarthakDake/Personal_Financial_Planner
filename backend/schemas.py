"""Pydantic request/response schemas — all client fields configurable."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Client profile (fully configurable) ───────────────────────────────────────

class PersonalDetailsSchema(BaseModel):
    full_name: str = ""
    age: int = Field(default=30, ge=18, le=100)
    retirement_age: int = Field(default=60, ge=30, le=80)
    life_expectancy: int = Field(default=85, ge=60, le=110)
    marital_status: str = "single"
    dependents: int = Field(default=0, ge=0)
    children: int = Field(default=0, ge=0)
    city_type: str = "metro"
    email: str = ""
    phone: str = ""
    pan: str = ""
    residential_status: str = "resident"


class IncomeSchema(BaseModel):
    salary_monthly: float = 0
    bonus_annual: float = 0
    business_income_annual: float = 0
    rental_income_monthly: float = 0
    other_income_annual: float = 0
    employer_epf_contribution_monthly: float = 0
    employee_epf_contribution_monthly: float = 0


class ExpensesSchema(BaseModel):
    monthly_living: float = 0
    travel_monthly: float = 0
    medical_monthly: float = 0
    education_monthly: float = 0
    insurance_premium_monthly: float = 0
    entertainment_monthly: float = 0
    miscellaneous_monthly: float = 0
    rent_monthly: float = 0


class LoanSchema(BaseModel):
    name: str
    loan_type: str = "other"
    principal_outstanding: float
    interest_rate_annual: float = Field(
        ...,
        description="Annual interest rate as a percentage, e.g. 8.5 for 8.5% (not 0.085)",
    )
    emi: float = Field(0, description="Monthly EMI amount in INR")
    tenure_months_remaining: int
    original_principal: float = 0
    prepayment_amount: float = 0
    start_date: Optional[str] = None


class AssetsSchema(BaseModel):
    savings: float = 0
    fd: float = 0
    ppf: float = 0
    epf: float = 0
    nps: float = 0
    mutual_funds: float = 0
    stocks: float = 0
    gold: float = 0
    real_estate: float = 0
    cash: float = 0
    emergency_fund: float = 0
    other: float = 0
    reit: float = 0
    invit: float = 0


class InsuranceSchema(BaseModel):
    health_cover: float = 0
    health_premium_annual: float = 0
    life_cover: float = 0
    life_premium_annual: float = 0
    accident_cover: float = 0
    accident_premium_annual: float = 0
    critical_illness_cover: float = 0
    critical_illness_premium_annual: float = 0


class InvestmentSchema(BaseModel):
    name: str
    category: str = "mutual_funds"
    amount: float = Field(0, description="Current invested amount / lumpsum corpus in INR")
    monthly_sip: float = Field(0, description="Monthly SIP amount in INR")
    expected_return: float = Field(
        12,
        description="Expected annual return as a percentage, e.g. 12 for 12% (not 0.12)",
    )
    start_date: Optional[str] = None
    is_lumpsum: bool = False


class GoalSchema(BaseModel):
    name: str
    goal_type: str = "custom"
    current_cost: float = Field(..., description="Today's cost of the goal in INR")
    target_year: int = Field(
        ...,
        description="Years from now (<100), age at goal (100-1900), or calendar year (>1900)",
    )
    priority: str = "medium"
    already_saved: float = Field(0, description="Amount already saved toward this goal in INR")
    inflation_rate: Optional[float] = Field(
        None, description="Goal inflation as %, e.g. 8 for 8%. Null = system default"
    )
    expected_return: Optional[float] = Field(
        None, description="Expected return as %, e.g. 12 for 12%. Null = risk-based default"
    )
    notes: str = ""


class TaxSchema(BaseModel):
    regime_preference: str = "new"
    hra_received_annual: float = 0
    rent_paid_annual: float = 0
    section_80c_investments: float = 0
    section_80ccd_1b: float = 0
    section_80d_self: float = 0
    section_80d_parents: float = 0
    home_loan_interest: float = 0
    is_senior_citizen: bool = False
    parents_senior_citizen: bool = False
    ltcg_equity: float = 0
    stcg_equity: float = 0
    other_deductions: float = 0


class AssumptionsSchema(BaseModel):
    """Optional overrides — all rates as percentages (6 = 6%). Zero/null = system default."""

    general_inflation: Optional[float] = Field(None, description="General inflation % p.a.")
    healthcare_inflation: Optional[float] = Field(None, description="Healthcare inflation % p.a.")
    education_inflation: Optional[float] = Field(None, description="Education inflation % p.a.")
    expected_equity_return: Optional[float] = Field(None, description="Expected equity return % p.a.")
    expected_debt_return: Optional[float] = Field(None, description="Expected debt return % p.a.")
    safe_withdrawal_rate: Optional[float] = Field(None, description="Safe withdrawal rate % p.a.")
    salary_growth_rate: Optional[float] = Field(None, description="Salary growth rate % p.a.")


class ClientProfileSchema(BaseModel):
    personal: PersonalDetailsSchema = Field(default_factory=PersonalDetailsSchema)
    income: IncomeSchema = Field(default_factory=IncomeSchema)
    expenses: ExpensesSchema = Field(default_factory=ExpensesSchema)
    loans: list[LoanSchema] = Field(default_factory=list)
    assets: AssetsSchema = Field(default_factory=AssetsSchema)
    insurance: InsuranceSchema = Field(default_factory=InsuranceSchema)
    investments: list[InvestmentSchema] = Field(default_factory=list)
    goals: list[GoalSchema] = Field(default_factory=list)
    tax: TaxSchema = Field(default_factory=TaxSchema)
    risk_profile: str = "moderate"
    risk_answers: dict[str, str] = Field(default_factory=dict)
    assumptions: AssumptionsSchema = Field(default_factory=AssumptionsSchema)


class ClientCreate(BaseModel):
    profile: ClientProfileSchema
    notes: str = ""


class ClientUpdate(BaseModel):
    profile: Optional[ClientProfileSchema] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ClientOut(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    risk_profile: str
    notes: str
    profile_data: dict[str, Any]
    created_at: Any
    updated_at: Any

    model_config = {"from_attributes": True}


class PlanGenerateRequest(BaseModel):
    client_id: Optional[str] = None
    profile: Optional[ClientProfileSchema] = None
    generate_excel: bool = True
    generate_pdf: bool = True
    generate_charts: bool = True
    save: bool = True


class WhatIfRequest(BaseModel):
    profile: ClientProfileSchema
    income_change_percent: float = 0
    expense_change_percent: float = 0
    sip_change_absolute: float = 0
    inflation_override: Optional[float] = None
    returns_override: Optional[float] = None
    loan_interest_change_percent: float = 0
    retirement_age_override: Optional[int] = None


class PlanOut(BaseModel):
    id: Optional[str] = None
    client_id: Optional[str] = None
    plan: dict[str, Any]
    excel_path: Optional[str] = None
    pdf_path: Optional[str] = None
    chart_paths: list[str] = Field(default_factory=list)
