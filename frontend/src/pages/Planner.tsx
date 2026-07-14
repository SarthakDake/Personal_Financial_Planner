import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  createClient,
  generatePlan,
  getClient,
  getDemoProfile,
  getRiskQuestionnaire,
  previewPlan,
  scoreRisk,
  seedDemoClient,
  updateClient,
} from '@/lib/api'
import { emptyProfile, type ClientProfile, type Goal, type Investment, type Loan } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatINR } from '@/lib/utils'
import { validateProfileForSave, validateStep } from '@/lib/validation'
import { Download, Play, Plus, Sparkles, Trash2 } from 'lucide-react'

const STEPS = [
  'Personal',
  'Income',
  'Expenses',
  'Loans',
  'Assets',
  'Insurance',
  'Investments',
  'Goals',
  'Tax',
  'Risk',
  'Assumptions',
  'Generate',
]

function Hint({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-stone-100/80 dark:bg-stone-900/50 px-3 py-2 text-xs text-stone-600 dark:text-stone-300 mb-4">
      {children}
    </div>
  )
}

function ErrorBox({ errors }: { errors: string[] }) {
  if (!errors.length) return null
  return (
    <div className="rounded-xl border border-danger/30 bg-red-50 dark:bg-red-950/30 px-3 py-2 text-xs text-danger space-y-1">
      <p className="font-semibold">Please fix the following:</p>
      <ul className="list-disc pl-4 space-y-0.5">
        {errors.map((e) => (
          <li key={e}>{e}</li>
        ))}
      </ul>
    </div>
  )
}

function Field({
  label,
  hint,
  children,
}: {
  label: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {hint && <p className="text-[11px] text-muted -mt-0.5">{hint}</p>}
      {children}
    </div>
  )
}

function NumInput({
  value,
  onChange,
  step = 1,
  suffix,
}: {
  value: number
  onChange: (v: number) => void
  step?: number
  suffix?: string
}) {
  return (
    <div className="relative">
      <Input
        type="number"
        step={step}
        value={Number.isFinite(value) ? value : 0}
        onChange={(e) => onChange(Number(e.target.value))}
        className={suffix ? 'pr-10' : undefined}
      />
      {suffix && (
        <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted">
          {suffix}
        </span>
      )}
    </div>
  )
}

export default function Planner() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const clientId = params.get('client')
  const [step, setStep] = useState(0)
  const [profile, setProfile] = useState<ClientProfile>(emptyProfile())
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [preview, setPreview] = useState<Record<string, unknown> | null>(null)
  const [reportMeta, setReportMeta] = useState<{ client_id?: string }>({})
  const [questionnaire, setQuestionnaire] = useState<{
    questions: Array<{ id: string; text: string; options: Array<{ id: string; text: string }> }>
  } | null>(null)
  const [riskResult, setRiskResult] = useState<Record<string, unknown> | null>(null)
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState<string[]>([])

  useEffect(() => {
    getRiskQuestionnaire().then(setQuestionnaire).catch(() => undefined)
    if (clientId) {
      getClient(clientId).then((c) => setProfile({ ...emptyProfile(), ...c.profile_data }))
    }
  }, [clientId])

  const title = useMemo(() => STEPS[step], [step])

  function updatePersonal<K extends keyof ClientProfile['personal']>(
    key: K,
    value: ClientProfile['personal'][K],
  ) {
    setProfile((p) => ({ ...p, personal: { ...p.personal, [key]: value } }))
  }

  async function loadDemo() {
    setMessage('')
    try {
      const demo = await getDemoProfile()
      setProfile({ ...emptyProfile(), ...demo })
      setMessage('Loaded Priya & Rohan Mehta demo profile. Review tabs, then Generate.')
      setStep(0)
    } catch (e: unknown) {
      setMessage(String((e as Error).message))
    }
  }

  async function seedAndOpenDemo() {
    setMessage('')
    try {
      const result = await seedDemoClient()
      setMessage(`Demo client ${result.action}: ${result.full_name}`)
      navigate(`/planner?client=${result.id}`)
    } catch (e: unknown) {
      setMessage(String((e as Error).message))
    }
  }

  function runStepValidation(targetStep = step): boolean {
    const result = validateStep(targetStep, profile)
    if (!result.ok) {
      setErrors(result.errors)
      setMessage('')
      return false
    }
    setErrors([])
    return true
  }

  async function saveClient() {
    const result = validateProfileForSave(profile)
    if (!result.ok) {
      setErrors(result.errors)
      setMessage('')
      return null
    }
    setSaving(true)
    setMessage('')
    setErrors([])
    try {
      if (clientId) {
        await updateClient(clientId, profile)
        setMessage('Client updated.')
        return clientId
      }
      const created = await createClient(profile)
      setMessage('Client created.')
      navigate(`/planner?client=${created.id}`, { replace: true })
      return created.id
    } catch (e: unknown) {
      setMessage(String((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || e))
      return null
    } finally {
      setSaving(false)
    }
  }

  async function runPreview() {
    const result = validateProfileForSave(profile)
    if (!result.ok) {
      setErrors(result.errors)
      return
    }
    setGenerating(true)
    setErrors([])
    try {
      const plan = await previewPlan(profile)
      setPreview(plan as unknown as Record<string, unknown>)
      setMessage('Preview calculated.')
    } catch (e: unknown) {
      setMessage(String((e as Error).message))
    } finally {
      setGenerating(false)
    }
  }

  async function runGenerate() {
    const result = validateProfileForSave(profile)
    if (!result.ok) {
      setErrors(result.errors)
      setMessage('')
      return
    }
    setGenerating(true)
    setMessage('')
    setErrors([])
    try {
      const id = (await saveClient()) || clientId || undefined
      if (!id && !profile.personal.full_name) return
      const gen = await generatePlan({
        client_id: id || undefined,
        profile: id ? undefined : profile,
        generate_excel: true,
        generate_pdf: true,
        generate_charts: true,
        save: Boolean(id),
      })
      setPreview(gen.plan as unknown as Record<string, unknown>)
      setReportMeta({ client_id: gen.client_id || id || undefined })
      setMessage('Full plan generated — dashboard, Excel, PDF, and charts ready.')
    } catch (e: unknown) {
      setMessage(String((e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || e))
    } finally {
      setGenerating(false)
    }
  }

  async function applyRiskAnswers(answers: Record<string, string>) {
    setProfile((p) => ({ ...p, risk_answers: answers }))
    const scored = await scoreRisk(answers)
    setRiskResult(scored)
    setProfile((p) => ({ ...p, risk_profile: String(scored.profile), risk_answers: answers }))
  }

  async function downloadFile(kind: 'excel' | 'pdf') {
    if (!reportMeta.client_id) return
    const token = localStorage.getItem('access_token')
    const res = await fetch(`/api/v1/planning/download/${kind}/${reportMeta.client_id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = kind === 'excel' ? 'Financial_Plan.xlsx' : 'Financial_Plan.pdf'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between animate-fade-up">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl text-navy dark:text-white">Client Planner</h1>
          <p className="mt-1 text-sm text-muted">
            Step {step + 1}/{STEPS.length}: {title}. Amounts show Monthly or Annual; rates use % (e.g. 8.5).
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={loadDemo}>
            <Sparkles className="h-4 w-4" /> Load Demo Form
          </Button>
          <Button variant="accent" size="sm" onClick={seedAndOpenDemo}>
            Save Demo Client
          </Button>
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-thin">
        {STEPS.map((s, i) => (
          <button
            key={s}
            onClick={() => setStep(i)}
            className={`shrink-0 rounded-lg px-2.5 py-1.5 text-[11px] sm:text-xs transition-colors ${
              i === step
                ? 'bg-navy text-white'
                : 'bg-white dark:bg-card-dark border border-border dark:border-border-dark text-muted'
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <Card className="animate-fade-up">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {step === 0 && (
            <>
              <Hint>Personal details identify the household. Ages are in years (not months).</Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Full Name">
                  <Input value={profile.personal.full_name} onChange={(e) => updatePersonal('full_name', e.target.value)} />
                </Field>
                <Field label="Email">
                  <Input value={profile.personal.email} onChange={(e) => updatePersonal('email', e.target.value)} />
                </Field>
                <Field label="Phone">
                  <Input value={profile.personal.phone} onChange={(e) => updatePersonal('phone', e.target.value)} />
                </Field>
                <Field label="PAN">
                  <Input value={profile.personal.pan} onChange={(e) => updatePersonal('pan', e.target.value)} />
                </Field>
                <Field label="Current Age" hint="Years">
                  <NumInput value={profile.personal.age} onChange={(v) => updatePersonal('age', v)} />
                </Field>
                <Field label="Retirement Age" hint="Years">
                  <NumInput value={profile.personal.retirement_age} onChange={(v) => updatePersonal('retirement_age', v)} />
                </Field>
                <Field label="Life Expectancy" hint="Years">
                  <NumInput value={profile.personal.life_expectancy} onChange={(v) => updatePersonal('life_expectancy', v)} />
                </Field>
                <Field label="Marital Status">
                  <select
                    className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                    value={profile.personal.marital_status}
                    onChange={(e) => updatePersonal('marital_status', e.target.value)}
                  >
                    {['single', 'married', 'divorced', 'widowed'].map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </Field>
                <Field label="Dependents" hint="Count of people financially dependent">
                  <NumInput value={profile.personal.dependents} onChange={(v) => updatePersonal('dependents', v)} />
                </Field>
                <Field label="Children" hint="Count">
                  <NumInput value={profile.personal.children} onChange={(v) => updatePersonal('children', v)} />
                </Field>
                <Field label="City Type" hint="Affects HRA & health cover recommendations">
                  <select
                    className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                    value={profile.personal.city_type}
                    onChange={(e) => updatePersonal('city_type', e.target.value)}
                  >
                    <option value="metro">Metro</option>
                    <option value="non_metro">Non-Metro</option>
                  </select>
                </Field>
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <Hint>
                Enter income in the period shown on each label. Monthly fields are multiplied by 12
                automatically for annual calculations.
              </Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                {(
                  [
                    ['salary_monthly', 'Salary (Monthly ₹)', 'Take-home / CTC monthly cash salary'],
                    ['bonus_annual', 'Bonus (Annual ₹)', 'Total expected bonus for the year'],
                    ['business_income_annual', 'Business Income (Annual ₹)', 'Net business / freelance income per year'],
                    ['rental_income_monthly', 'Rental Income (Monthly ₹)', 'Monthly rent received'],
                    ['other_income_annual', 'Other Income (Annual ₹)', 'Interest, dividends, etc. per year'],
                    ['employee_epf_contribution_monthly', 'Employee EPF (Monthly ₹)', 'Your monthly EPF contribution'],
                    ['employer_epf_contribution_monthly', 'Employer EPF (Monthly ₹)', 'Employer monthly EPF contribution'],
                  ] as const
                ).map(([key, label, hint]) => (
                  <Field key={key} label={label} hint={hint}>
                    <NumInput
                      value={profile.income[key]}
                      onChange={(v) => setProfile((p) => ({ ...p, income: { ...p.income, [key]: v } }))}
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <Hint>All expense fields below are Monthly amounts in ₹.</Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                {(
                  [
                    ['monthly_living', 'Living Expenses (Monthly ₹)'],
                    ['travel_monthly', 'Travel (Monthly ₹)'],
                    ['medical_monthly', 'Medical (Monthly ₹)'],
                    ['education_monthly', 'Education (Monthly ₹)'],
                    ['insurance_premium_monthly', 'Insurance Premiums (Monthly ₹)'],
                    ['entertainment_monthly', 'Entertainment (Monthly ₹)'],
                    ['miscellaneous_monthly', 'Miscellaneous (Monthly ₹)'],
                    ['rent_monthly', 'House Rent Paid (Monthly ₹)'],
                  ] as const
                ).map(([key, label]) => (
                  <Field key={key} label={label}>
                    <NumInput
                      value={profile.expenses[key]}
                      onChange={(v) => setProfile((p) => ({ ...p, expenses: { ...p.expenses, [key]: v } }))}
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <Hint>
                Outstanding & prepayment are lump-sum ₹. EMI is Monthly ₹. Interest rate is Annual %
                (enter 8.5 for 8.5%, not 0.085).
              </Hint>
              <div className="space-y-4">
                {profile.loans.map((loan, idx) => (
                  <div key={idx} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 border border-border/60 rounded-xl p-4">
                    <Field label="Loan Name">
                      <Input
                        value={loan.name}
                        onChange={(e) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, name: e.target.value }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <Field label="Loan Type">
                      <select
                        className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                        value={loan.loan_type}
                        onChange={(e) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, loan_type: e.target.value }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      >
                        {['home', 'car', 'personal', 'education', 'gold', 'credit_card', 'other'].map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Outstanding Principal (₹)" hint="Current balance — lump sum">
                      <NumInput
                        value={loan.principal_outstanding}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, principal_outstanding: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <Field label="Interest Rate (Annual %)" hint="Example: 8.5 means 8.5% p.a.">
                      <NumInput
                        step={0.1}
                        suffix="%"
                        value={loan.interest_rate_annual}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, interest_rate_annual: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <Field label="EMI (Monthly ₹)">
                      <NumInput
                        value={loan.emi}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, emi: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <Field label="Tenure Remaining (Months)">
                      <NumInput
                        value={loan.tenure_months_remaining}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, tenure_months_remaining: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <Field label="Planned Prepayment (₹)" hint="Optional one-time lump sum">
                      <NumInput
                        value={loan.prepayment_amount}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, prepayment_amount: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                    <div className="flex items-end">
                      <Button
                        variant="ghost"
                        onClick={() =>
                          setProfile((p) => ({ ...p, loans: p.loans.filter((_, i) => i !== idx) }))
                        }
                      >
                        <Trash2 className="h-4 w-4" /> Remove
                      </Button>
                    </div>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() =>
                    setProfile((p) => ({
                      ...p,
                      loans: [
                        ...p.loans,
                        {
                          name: 'New Loan',
                          loan_type: 'personal',
                          principal_outstanding: 0,
                          interest_rate_annual: 10,
                          emi: 0,
                          tenure_months_remaining: 12,
                          original_principal: 0,
                          prepayment_amount: 0,
                        } satisfies Loan,
                      ],
                    }))
                  }
                >
                  <Plus className="h-4 w-4" /> Add Loan
                </Button>
              </div>
            </>
          )}

          {step === 4 && (
            <>
              <Hint>Enter current market value / balance for each asset in ₹ (lump-sum balances, not monthly).</Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                {(
                  [
                    ['savings', 'Bank Savings (₹)'],
                    ['cash', 'Cash in Hand (₹)'],
                    ['emergency_fund', 'Emergency Fund (₹)'],
                    ['fd', 'Fixed Deposits (₹)'],
                    ['ppf', 'PPF Balance (₹)'],
                    ['epf', 'EPF Balance (₹)'],
                    ['nps', 'NPS Balance (₹)'],
                    ['mutual_funds', 'Mutual Funds (₹)'],
                    ['stocks', 'Stocks / Equity (₹)'],
                    ['gold', 'Gold (₹)'],
                    ['reit', 'REITs (₹)'],
                    ['invit', 'InvITs (₹)'],
                    ['real_estate', 'Real Estate (₹)'],
                    ['other', 'Other Assets (₹)'],
                  ] as const
                ).map(([key, label]) => (
                  <Field key={key} label={label}>
                    <NumInput
                      value={profile.assets[key]}
                      onChange={(v) => setProfile((p) => ({ ...p, assets: { ...p.assets, [key]: v } }))}
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 5 && (
            <>
              <Hint>
                Cover amounts are sum assured in ₹. Premium fields are Annual ₹ (yearly premium paid).
              </Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                {(
                  [
                    ['health_cover', 'Health Cover / Sum Assured (₹)'],
                    ['health_premium_annual', 'Health Premium (Annual ₹)'],
                    ['life_cover', 'Life Cover / Sum Assured (₹)'],
                    ['life_premium_annual', 'Life Premium (Annual ₹)'],
                    ['accident_cover', 'Accident Cover (₹)'],
                    ['accident_premium_annual', 'Accident Premium (Annual ₹)'],
                    ['critical_illness_cover', 'Critical Illness Cover (₹)'],
                    ['critical_illness_premium_annual', 'Critical Illness Premium (Annual ₹)'],
                  ] as const
                ).map(([key, label]) => (
                  <Field key={key} label={label}>
                    <NumInput
                      value={profile.insurance[key]}
                      onChange={(v) =>
                        setProfile((p) => ({ ...p, insurance: { ...p.insurance, [key]: v } }))
                      }
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 6 && (
            <>
              <Hint>
                Amount = current corpus (₹ lump sum). SIP = Monthly ₹. Expected return = Annual %
                (enter 12 for 12%, not 0.12).
              </Hint>
              <div className="space-y-4">
                {profile.investments.map((inv, idx) => (
                  <div key={idx} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 border border-border/60 rounded-xl p-4">
                    <Field label="Investment Name">
                      <Input
                        value={inv.name}
                        onChange={(e) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, name: e.target.value }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                    <Field label="Category">
                      <Input
                        value={inv.category}
                        onChange={(e) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, category: e.target.value }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                    <Field label="Current Amount / Corpus (₹)">
                      <NumInput
                        value={inv.amount}
                        onChange={(v) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, amount: v }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                    <Field label="SIP (Monthly ₹)">
                      <NumInput
                        value={inv.monthly_sip}
                        onChange={(v) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, monthly_sip: v }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                    <Field label="Expected Return (Annual %)" hint="Example: 12 means 12% p.a.">
                      <NumInput
                        step={0.1}
                        suffix="%"
                        value={inv.expected_return}
                        onChange={(v) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, expected_return: v }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                    <div className="flex items-end">
                      <Button
                        variant="ghost"
                        onClick={() =>
                          setProfile((p) => ({
                            ...p,
                            investments: p.investments.filter((_, i) => i !== idx),
                          }))
                        }
                      >
                        <Trash2 className="h-4 w-4" /> Remove
                      </Button>
                    </div>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() =>
                    setProfile((p) => ({
                      ...p,
                      investments: [
                        ...p.investments,
                        {
                          name: 'New SIP',
                          category: 'mutual_funds',
                          amount: 0,
                          monthly_sip: 0,
                          expected_return: 12,
                          is_lumpsum: false,
                        } satisfies Investment,
                      ],
                    }))
                  }
                >
                  <Plus className="h-4 w-4" /> Add Investment
                </Button>
              </div>
            </>
          )}

          {step === 7 && (
            <>
              <Hint>
                Current cost = today&apos;s price in ₹. Target = years from now (e.g. 5), or age, or
                calendar year. Inflation & return overrides use Annual % (8 = 8%).
              </Hint>
              <div className="space-y-4">
                {profile.goals.map((goal, idx) => (
                  <div key={idx} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 border border-border/60 rounded-xl p-4">
                    <Field label="Goal Name">
                      <Input
                        value={goal.name}
                        onChange={(e) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, name: e.target.value }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <Field label="Goal Type">
                      <select
                        className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                        value={goal.goal_type}
                        onChange={(e) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, goal_type: e.target.value }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      >
                        {[
                          'house', 'car', 'children_education', 'children_marriage',
                          'retirement', 'vacation', 'emergency', 'business', 'custom',
                        ].map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Priority">
                      <select
                        className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                        value={goal.priority}
                        onChange={(e) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, priority: e.target.value }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      >
                        {['high', 'medium', 'low'].map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Current Cost (Today's ₹)">
                      <NumInput
                        value={goal.current_cost}
                        onChange={(v) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, current_cost: v }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <Field label="Years from Now / Age / Year" hint="e.g. 5 = in 5 years">
                      <NumInput
                        value={goal.target_year}
                        onChange={(v) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, target_year: v }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <Field label="Already Saved (₹)">
                      <NumInput
                        value={goal.already_saved}
                        onChange={(v) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, already_saved: v }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <Field label="Inflation Override (Annual %)" hint="Optional — leave 0 for default">
                      <NumInput
                        step={0.1}
                        suffix="%"
                        value={Number(goal.inflation_rate || 0)}
                        onChange={(v) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, inflation_rate: v || null }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <Field label="Expected Return Override (Annual %)" hint="Optional">
                      <NumInput
                        step={0.1}
                        suffix="%"
                        value={Number(goal.expected_return || 0)}
                        onChange={(v) => {
                          const goals = [...profile.goals]
                          goals[idx] = { ...goal, expected_return: v || null }
                          setProfile((p) => ({ ...p, goals }))
                        }}
                      />
                    </Field>
                    <div className="flex items-end">
                      <Button
                        variant="ghost"
                        onClick={() =>
                          setProfile((p) => ({ ...p, goals: p.goals.filter((_, i) => i !== idx) }))
                        }
                      >
                        <Trash2 className="h-4 w-4" /> Remove
                      </Button>
                    </div>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() =>
                    setProfile((p) => ({
                      ...p,
                      goals: [
                        ...p.goals,
                        {
                          name: 'New Goal',
                          goal_type: 'custom',
                          current_cost: 0,
                          target_year: 5,
                          priority: 'medium',
                          already_saved: 0,
                          inflation_rate: null,
                          expected_return: null,
                          notes: '',
                        } satisfies Goal,
                      ],
                    }))
                  }
                >
                  <Plus className="h-4 w-4" /> Add Goal
                </Button>
              </div>
            </>
          )}

          {step === 8 && (
            <>
              <Hint>All tax amount fields are Annual ₹ for the current financial year.</Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Regime Preference">
                  <select
                    className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                    value={profile.tax.regime_preference}
                    onChange={(e) =>
                      setProfile((p) => ({
                        ...p,
                        tax: { ...p.tax, regime_preference: e.target.value },
                      }))
                    }
                  >
                    <option value="new">New</option>
                    <option value="old">Old</option>
                  </select>
                </Field>
                {(
                  [
                    ['hra_received_annual', 'HRA Received (Annual ₹)'],
                    ['rent_paid_annual', 'Rent Paid (Annual ₹)'],
                    ['section_80c_investments', 'Section 80C Investments (Annual ₹)'],
                    ['section_80ccd_1b', 'Section 80CCD(1B) NPS (Annual ₹)'],
                    ['section_80d_self', 'Section 80D Self (Annual ₹)'],
                    ['section_80d_parents', 'Section 80D Parents (Annual ₹)'],
                    ['home_loan_interest', 'Home Loan Interest Claimed (Annual ₹)'],
                    ['ltcg_equity', 'LTCG Equity (Annual ₹)'],
                    ['stcg_equity', 'STCG Equity (Annual ₹)'],
                    ['other_deductions', 'Other Deductions (Annual ₹)'],
                  ] as const
                ).map(([key, label]) => (
                  <Field key={key} label={label}>
                    <NumInput
                      value={profile.tax[key] as number}
                      onChange={(v) => setProfile((p) => ({ ...p, tax: { ...p.tax, [key]: v } }))}
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 9 && (
            <div className="space-y-4">
              <Hint>Complete the questionnaire or set a manual risk profile. No money amounts here.</Hint>
              <Field label="Manual Risk Profile">
                <select
                  className="h-10 w-full max-w-xs rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                  value={profile.risk_profile}
                  onChange={(e) => setProfile((p) => ({ ...p, risk_profile: e.target.value }))}
                >
                  {['conservative', 'moderate', 'aggressive'].map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
              </Field>
              {questionnaire && (
                <div className="space-y-4">
                  {questionnaire.questions.map((q) => (
                    <div key={q.id} className="space-y-2">
                      <Label>{q.text}</Label>
                      <select
                        className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                        value={profile.risk_answers[q.id] || ''}
                        onChange={async (e) => {
                          const answers = { ...profile.risk_answers, [q.id]: e.target.value }
                          const complete = questionnaire.questions.every((qq) => answers[qq.id])
                          setProfile((p) => ({ ...p, risk_answers: answers }))
                          if (complete) await applyRiskAnswers(answers)
                        }}
                      >
                        <option value="">Select…</option>
                        {q.options.map((o) => (
                          <option key={o.id} value={o.id}>{o.text}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
              {riskResult && (
                <div className="rounded-xl bg-surface dark:bg-navy-deep p-4 text-sm">
                  Profile: <b>{String(riskResult.profile)}</b> · Personality:{' '}
                  <b>{String(riskResult.personality)}</b> · Score: {String(riskResult.total_score)}
                </div>
              )}
            </div>
          )}

          {step === 10 && (
            <>
              <Hint>
                All assumption rates are Annual %. Enter 6 for 6% inflation — not 0.06. Leave at 0 to
                use system defaults from config.
              </Hint>
              <div className="grid gap-4 sm:grid-cols-2">
                {(
                  [
                    ['general_inflation', 'General Inflation (Annual %)'],
                    ['healthcare_inflation', 'Healthcare Inflation (Annual %)'],
                    ['education_inflation', 'Education Inflation (Annual %)'],
                    ['expected_equity_return', 'Expected Equity Return (Annual %)'],
                    ['expected_debt_return', 'Expected Debt Return (Annual %)'],
                    ['safe_withdrawal_rate', 'Safe Withdrawal Rate (Annual %)'],
                    ['salary_growth_rate', 'Salary Growth Rate (Annual %)'],
                  ] as const
                ).map(([key, label]) => (
                  <Field key={key} label={label}>
                    <NumInput
                      step={0.1}
                      suffix="%"
                      value={Number(profile.assumptions[key] ?? 0)}
                      onChange={(v) =>
                        setProfile((p) => ({
                          ...p,
                          assumptions: { ...p.assumptions, [key]: v || null },
                        }))
                      }
                    />
                  </Field>
                ))}
              </div>
            </>
          )}

          {step === 11 && (
            <div className="space-y-4">
              <Hint>
                One click generates dashboard metrics, Excel workbook, PDF plan, charts, and
                recommendations for this client.
              </Hint>
              <div className="flex flex-wrap gap-3">
                <Button onClick={saveClient} disabled={saving} variant="outline">
                  {saving ? 'Saving…' : 'Save Client'}
                </Button>
                <Button onClick={runPreview} disabled={generating} variant="outline">
                  Preview Calculations
                </Button>
                <Button onClick={runGenerate} disabled={generating}>
                  <Play className="h-4 w-4" />
                  {generating ? 'Generating…' : 'Generate Full Plan'}
                </Button>
              </div>
              <ErrorBox errors={errors} />
              {message && <p className="text-sm text-stone-600 dark:text-stone-300">{message}</p>}
              {preview && (
                <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
                  {[
                    ['Net Worth', formatINR(Number((preview.summary as Record<string, unknown>)?.net_worth || 0))],
                    ['Health Score', String((preview.health_score as Record<string, unknown>)?.score ?? '—')],
                    [
                      'Retirement Progress',
                      `${(preview.retirement as Record<string, unknown>)?.progress_percent ?? 0}%`,
                    ],
                    [
                      'Monthly Surplus',
                      formatINR(Number((preview.cash_flow as Record<string, unknown>)?.monthly_surplus || 0)),
                    ],
                  ].map(([k, v]) => (
                    <div key={k} className="rounded-xl border border-border/60 p-4">
                      <div className="text-xs text-muted uppercase">{k}</div>
                      <div className="mt-1 text-lg font-semibold break-words">{v}</div>
                    </div>
                  ))}
                </div>
              )}
              {reportMeta.client_id && (
                <div className="flex flex-wrap gap-3">
                  <Button variant="accent" onClick={() => downloadFile('excel')}>
                    <Download className="h-4 w-4" /> Download Excel
                  </Button>
                  <Button variant="accent" onClick={() => downloadFile('pdf')}>
                    <Download className="h-4 w-4" /> Download PDF
                  </Button>
                </div>
              )}
            </div>
          )}

          <ErrorBox errors={errors} />
          {message && step !== 11 && <p className="text-sm text-stone-600 dark:text-stone-300">{message}</p>}

          <div className="flex justify-between pt-4 border-t border-border/50 gap-2">
            <Button
              variant="outline"
              disabled={step === 0}
              onClick={() => {
                setErrors([])
                setStep((s) => s - 1)
              }}
            >
              Back
            </Button>
            <Button
              disabled={step === STEPS.length - 1}
              onClick={() => {
                if (!runStepValidation(step)) return
                setStep((s) => s + 1)
              }}
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
