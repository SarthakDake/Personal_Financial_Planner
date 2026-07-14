import { z } from 'zod'
import type { ClientProfile } from '@/types'

/** Per-step validation for the client planner wizard. */

export const personalSchema = z
  .object({
    full_name: z.string().trim().min(2, 'Full name is required (min 2 characters)'),
    age: z.number().int().min(18, 'Age must be at least 18').max(100, 'Age must be ≤ 100'),
    retirement_age: z
      .number()
      .int()
      .min(30, 'Retirement age must be at least 30')
      .max(80, 'Retirement age must be ≤ 80'),
    life_expectancy: z.number().int().min(60).max(110),
    email: z
      .string()
      .email('Enter a valid email')
      .or(z.literal(''))
      .optional(),
    phone: z.string().optional(),
    pan: z.string().optional(),
    marital_status: z.string().min(1),
    dependents: z.number().int().min(0),
    children: z.number().int().min(0),
    city_type: z.string().min(1),
    residential_status: z.string().optional(),
  })
  .refine((d) => d.retirement_age > d.age, {
    message: 'Retirement age must be greater than current age',
    path: ['retirement_age'],
  })
  .refine((d) => d.life_expectancy > d.retirement_age, {
    message: 'Life expectancy must be greater than retirement age',
    path: ['life_expectancy'],
  })

export const incomeSchema = z
  .object({
    salary_monthly: z.number().min(0),
    bonus_annual: z.number().min(0),
    business_income_annual: z.number().min(0),
    rental_income_monthly: z.number().min(0),
    other_income_annual: z.number().min(0),
    employer_epf_contribution_monthly: z.number().min(0),
    employee_epf_contribution_monthly: z.number().min(0),
  })
  .refine(
    (d) =>
      d.salary_monthly +
        d.bonus_annual / 12 +
        d.business_income_annual / 12 +
        d.rental_income_monthly +
        d.other_income_annual / 12 >
      0,
    { message: 'Enter at least one income source greater than zero', path: ['salary_monthly'] },
  )

export const expensesSchema = z.object({
  monthly_living: z.number().min(1, 'Monthly living expenses are required'),
  travel_monthly: z.number().min(0),
  medical_monthly: z.number().min(0),
  education_monthly: z.number().min(0),
  insurance_premium_monthly: z.number().min(0),
  entertainment_monthly: z.number().min(0),
  miscellaneous_monthly: z.number().min(0),
  rent_monthly: z.number().min(0),
})

export const loanItemSchema = z.object({
  name: z.string().trim().min(1, 'Loan name is required'),
  loan_type: z.string().min(1),
  principal_outstanding: z.number().positive('Outstanding principal must be > 0'),
  interest_rate_annual: z
    .number()
    .positive('Interest rate (%) is required')
    .max(100, 'Interest rate looks too high'),
  emi: z.number().positive('Monthly EMI must be > 0'),
  tenure_months_remaining: z.number().int().positive('Tenure (months) is required'),
  original_principal: z.number().min(0),
  prepayment_amount: z.number().min(0),
})

export const investmentItemSchema = z.object({
  name: z.string().trim().min(1, 'Investment name is required'),
  category: z.string().min(1, 'Category is required'),
  amount: z.number().min(0),
  monthly_sip: z.number().min(0),
  expected_return: z
    .number()
    .positive('Expected return (%) is required')
    .max(100, 'Expected return looks too high'),
  is_lumpsum: z.boolean(),
})

export const goalItemSchema = z.object({
  name: z.string().trim().min(1, 'Goal name is required'),
  goal_type: z.string().min(1),
  current_cost: z.number().min(0, 'Current cost cannot be negative'),
  target_year: z.number().int().positive('Target years / age / year is required'),
  priority: z.string().min(1),
  already_saved: z.number().min(0),
  inflation_rate: z.number().nullable().optional(),
  expected_return: z.number().nullable().optional(),
  notes: z.string().optional(),
})

export const taxSchema = z.object({
  regime_preference: z.enum(['old', 'new']),
  hra_received_annual: z.number().min(0),
  rent_paid_annual: z.number().min(0),
  section_80c_investments: z.number().min(0),
  section_80ccd_1b: z.number().min(0),
  section_80d_self: z.number().min(0),
  section_80d_parents: z.number().min(0),
  home_loan_interest: z.number().min(0),
  is_senior_citizen: z.boolean(),
  parents_senior_citizen: z.boolean(),
  ltcg_equity: z.number().min(0),
  stcg_equity: z.number().min(0),
  other_deductions: z.number().min(0),
})

export const riskSchema = z.object({
  risk_profile: z.enum(['conservative', 'moderate', 'aggressive'], {
    message: 'Select a risk profile',
  }),
})

export type ValidationResult = { ok: true } | { ok: false; errors: string[] }

function formatZodErrors(err: z.ZodError): string[] {
  return err.issues.map((i) => i.message)
}

/** Validate a single wizard step (0–11). Empty list steps allow zero items. */
export function validateStep(step: number, profile: ClientProfile): ValidationResult {
  try {
    switch (step) {
      case 0:
        personalSchema.parse(profile.personal)
        break
      case 1:
        incomeSchema.parse(profile.income)
        break
      case 2:
        expensesSchema.parse(profile.expenses)
        break
      case 3:
        for (const loan of profile.loans) loanItemSchema.parse(loan)
        break
      case 4:
        // Assets optional but non-negative
        Object.values(profile.assets).forEach((v) => {
          if (typeof v === 'number' && v < 0) throw new Error('Asset values cannot be negative')
        })
        break
      case 5:
        Object.values(profile.insurance).forEach((v) => {
          if (typeof v === 'number' && v < 0) throw new Error('Insurance values cannot be negative')
        })
        break
      case 6:
        for (const inv of profile.investments) investmentItemSchema.parse(inv)
        break
      case 7:
        for (const goal of profile.goals) {
          goalItemSchema.parse(goal)
          if (goal.goal_type !== 'retirement' && goal.current_cost <= 0) {
            throw new z.ZodError([
              {
                code: 'custom',
                message: `Goal "${goal.name}" needs a current cost > 0`,
                path: ['current_cost'],
              },
            ])
          }
        }
        break
      case 8:
        taxSchema.parse(profile.tax)
        break
      case 9:
        riskSchema.parse({ risk_profile: profile.risk_profile })
        break
      case 10:
        // Assumptions optional; if set must be sensible %
        for (const [key, val] of Object.entries(profile.assumptions)) {
          if (val != null && val !== 0 && (Number(val) < 0 || Number(val) > 100)) {
            throw new Error(`${key.replace(/_/g, ' ')} must be between 0 and 100%`)
          }
        }
        break
      default:
        break
    }
    return { ok: true }
  } catch (e) {
    if (e instanceof z.ZodError) return { ok: false, errors: formatZodErrors(e) }
    return { ok: false, errors: [String((e as Error).message || e)] }
  }
}

/** Validate all critical steps before save / generate. */
export function validateProfileForSave(profile: ClientProfile): ValidationResult {
  const errors: string[] = []
  for (const step of [0, 1, 2, 9]) {
    const result = validateStep(step, profile)
    if (!result.ok) errors.push(...result.errors)
  }
  // Validate any populated list items
  for (const step of [3, 6, 7]) {
    const result = validateStep(step, profile)
    if (!result.ok) errors.push(...result.errors)
  }
  if (errors.length) return { ok: false, errors: [...new Set(errors)] }
  return { ok: true }
}
