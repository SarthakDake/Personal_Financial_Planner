export interface PersonalDetails {
  full_name: string
  age: number
  retirement_age: number
  life_expectancy: number
  marital_status: string
  dependents: number
  children: number
  city_type: string
  email: string
  phone: string
  pan: string
  residential_status: string
}

export interface Income {
  /** INR per month */
  salary_monthly: number
  /** INR per year */
  bonus_annual: number
  /** INR per year */
  business_income_annual: number
  /** INR per month */
  rental_income_monthly: number
  /** INR per year */
  other_income_annual: number
  /** INR per month */
  employer_epf_contribution_monthly: number
  /** INR per month */
  employee_epf_contribution_monthly: number
}

export interface Expenses {
  /** All expense fields are INR per month */
  monthly_living: number
  travel_monthly: number
  medical_monthly: number
  education_monthly: number
  insurance_premium_monthly: number
  entertainment_monthly: number
  miscellaneous_monthly: number
  rent_monthly: number
}

export interface Loan {
  name: string
  loan_type: string
  /** Outstanding principal in INR */
  principal_outstanding: number
  /** Annual interest rate as percentage, e.g. 8.5 for 8.5% */
  interest_rate_annual: number
  /** Monthly EMI in INR */
  emi: number
  tenure_months_remaining: number
  original_principal: number
  /** One-time prepayment amount in INR */
  prepayment_amount: number
}

export interface Assets {
  /** All asset fields are current balances in INR */
  savings: number
  fd: number
  ppf: number
  epf: number
  nps: number
  mutual_funds: number
  stocks: number
  gold: number
  real_estate: number
  cash: number
  emergency_fund: number
  other: number
  reit: number
  invit: number
}

export interface Insurance {
  health_cover: number
  /** INR per year */
  health_premium_annual: number
  life_cover: number
  /** INR per year */
  life_premium_annual: number
  accident_cover: number
  /** INR per year */
  accident_premium_annual: number
  critical_illness_cover: number
  /** INR per year */
  critical_illness_premium_annual: number
}

export interface Investment {
  name: string
  category: string
  /** Current corpus / lumpsum in INR */
  amount: number
  /** Monthly SIP in INR */
  monthly_sip: number
  /** Expected annual return as percentage, e.g. 12 for 12% */
  expected_return: number
  is_lumpsum: boolean
}

export interface Goal {
  name: string
  goal_type: string
  /** Today's cost in INR */
  current_cost: number
  /** Years from now (<100), age, or calendar year */
  target_year: number
  priority: string
  already_saved: number
  /** Optional inflation override as %, e.g. 8 */
  inflation_rate?: number | null
  /** Optional expected return as %, e.g. 12 */
  expected_return?: number | null
  notes: string
}

export interface TaxInputs {
  regime_preference: string
  /** All tax INR fields below are annual */
  hra_received_annual: number
  rent_paid_annual: number
  section_80c_investments: number
  section_80ccd_1b: number
  section_80d_self: number
  section_80d_parents: number
  home_loan_interest: number
  is_senior_citizen: boolean
  parents_senior_citizen: boolean
  ltcg_equity: number
  stcg_equity: number
  other_deductions: number
}

export interface Assumptions {
  /** All rates as percentages, e.g. 6 for 6%. Null/0 = system default */
  general_inflation?: number | null
  healthcare_inflation?: number | null
  education_inflation?: number | null
  expected_equity_return?: number | null
  expected_debt_return?: number | null
  safe_withdrawal_rate?: number | null
  salary_growth_rate?: number | null
}

export interface ClientProfile {
  personal: PersonalDetails
  income: Income
  expenses: Expenses
  loans: Loan[]
  assets: Assets
  insurance: Insurance
  investments: Investment[]
  goals: Goal[]
  tax: TaxInputs
  risk_profile: string
  risk_answers: Record<string, string>
  assumptions: Assumptions
}

export interface Client {
  id: string
  full_name: string
  email: string
  phone: string
  risk_profile: string
  notes: string
  profile_data: ClientProfile
  created_at: string
  updated_at: string
}

export interface PlanResult {
  summary: Record<string, unknown>
  net_worth: Record<string, number>
  cash_flow: Record<string, unknown>
  ratios: Record<string, unknown>
  emergency_fund: Record<string, unknown>
  goals: Array<Record<string, unknown>>
  retirement: Record<string, unknown>
  loans: Array<Record<string, unknown>>
  tax: Record<string, unknown>
  insurance: Record<string, unknown>
  risk: Record<string, unknown>
  recommendations: Record<string, unknown>
  portfolio: Record<string, unknown>
  health_score: Record<string, unknown>
  scenarios: Record<string, unknown>
  estate_checklist: Array<Record<string, unknown>>
  fire: Record<string, unknown>
  assumptions_used: Record<string, unknown>
}

export const emptyProfile = (): ClientProfile => ({
  personal: {
    full_name: '',
    age: 30,
    retirement_age: 60,
    life_expectancy: 85,
    marital_status: 'single',
    dependents: 0,
    children: 0,
    city_type: 'metro',
    email: '',
    phone: '',
    pan: '',
    residential_status: 'resident',
  },
  income: {
    salary_monthly: 0,
    bonus_annual: 0,
    business_income_annual: 0,
    rental_income_monthly: 0,
    other_income_annual: 0,
    employer_epf_contribution_monthly: 0,
    employee_epf_contribution_monthly: 0,
  },
  expenses: {
    monthly_living: 0,
    travel_monthly: 0,
    medical_monthly: 0,
    education_monthly: 0,
    insurance_premium_monthly: 0,
    entertainment_monthly: 0,
    miscellaneous_monthly: 0,
    rent_monthly: 0,
  },
  loans: [],
  assets: {
    savings: 0,
    fd: 0,
    ppf: 0,
    epf: 0,
    nps: 0,
    mutual_funds: 0,
    stocks: 0,
    gold: 0,
    real_estate: 0,
    cash: 0,
    emergency_fund: 0,
    other: 0,
    reit: 0,
    invit: 0,
  },
  insurance: {
    health_cover: 0,
    health_premium_annual: 0,
    life_cover: 0,
    life_premium_annual: 0,
    accident_cover: 0,
    accident_premium_annual: 0,
    critical_illness_cover: 0,
    critical_illness_premium_annual: 0,
  },
  investments: [],
  goals: [],
  tax: {
    regime_preference: 'new',
    hra_received_annual: 0,
    rent_paid_annual: 0,
    section_80c_investments: 0,
    section_80ccd_1b: 0,
    section_80d_self: 0,
    section_80d_parents: 0,
    home_loan_interest: 0,
    is_senior_citizen: false,
    parents_senior_citizen: false,
    ltcg_equity: 0,
    stcg_equity: 0,
    other_deductions: 0,
  },
  risk_profile: 'moderate',
  risk_answers: {},
  assumptions: {},
})
