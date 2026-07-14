import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  createClient,
  generatePlan,
  getClient,
  getRiskQuestionnaire,
  previewPlan,
  scoreRisk,
  updateClient,
} from '@/lib/api'
import { emptyProfile, type ClientProfile, type Goal, type Investment, type Loan } from '@/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatINR } from '@/lib/utils'
import { Download, Play, Plus, Trash2 } from 'lucide-react'

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

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
    </div>
  )
}

function NumInput({
  value,
  onChange,
  step = 1,
}: {
  value: number
  onChange: (v: number) => void
  step?: number
}) {
  return (
    <Input
      type="number"
      step={step}
      value={Number.isFinite(value) ? value : 0}
      onChange={(e) => onChange(Number(e.target.value))}
    />
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
  const [reportMeta, setReportMeta] = useState<{ client_id?: string; excel?: string; pdf?: string }>({})
  const [questionnaire, setQuestionnaire] = useState<{
    questions: Array<{ id: string; text: string; options: Array<{ id: string; text: string }> }>
  } | null>(null)
  const [riskResult, setRiskResult] = useState<Record<string, unknown> | null>(null)
  const [message, setMessage] = useState('')

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

  async function saveClient() {
    setSaving(true)
    setMessage('')
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
    setGenerating(true)
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
    setGenerating(true)
    setMessage('')
    try {
      const id = (await saveClient()) || clientId || undefined
      const result = await generatePlan({
        client_id: id || undefined,
        profile: id ? undefined : profile,
        generate_excel: true,
        generate_pdf: true,
        generate_charts: true,
        save: Boolean(id),
      })
      setPreview(result.plan as unknown as Record<string, unknown>)
      setReportMeta({
        client_id: result.client_id || id || undefined,
        excel: result.excel_path,
        pdf: result.pdf_path,
      })
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

  return (
    <div className="space-y-6">
      <div className="animate-fade-up">
        <h1 className="font-display text-4xl text-navy dark:text-white">Client Planner</h1>
        <p className="mt-1 text-sm text-muted">
          Fully configurable inputs for any individual or family. Step {step + 1} of {STEPS.length}: {title}
        </p>
      </div>

      <div className="flex gap-1 overflow-x-auto pb-1">
        {STEPS.map((s, i) => (
          <button
            key={s}
            onClick={() => setStep(i)}
            className={`shrink-0 rounded-lg px-3 py-1.5 text-xs transition-colors ${
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
            <div className="grid gap-4 md:grid-cols-2">
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
              <Field label="Age">
                <NumInput value={profile.personal.age} onChange={(v) => updatePersonal('age', v)} />
              </Field>
              <Field label="Retirement Age">
                <NumInput value={profile.personal.retirement_age} onChange={(v) => updatePersonal('retirement_age', v)} />
              </Field>
              <Field label="Life Expectancy">
                <NumInput value={profile.personal.life_expectancy} onChange={(v) => updatePersonal('life_expectancy', v)} />
              </Field>
              <Field label="Marital Status">
                <select
                  className="h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                  value={profile.personal.marital_status}
                  onChange={(e) => updatePersonal('marital_status', e.target.value)}
                >
                  {['single', 'married', 'divorced', 'widowed'].map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Dependents">
                <NumInput value={profile.personal.dependents} onChange={(v) => updatePersonal('dependents', v)} />
              </Field>
              <Field label="Children">
                <NumInput value={profile.personal.children} onChange={(v) => updatePersonal('children', v)} />
              </Field>
              <Field label="City Type">
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
          )}

          {step === 1 && (
            <div className="grid gap-4 md:grid-cols-2">
              {(
                [
                  ['salary_monthly', 'Monthly Salary'],
                  ['bonus_annual', 'Annual Bonus'],
                  ['business_income_annual', 'Business Income (Annual)'],
                  ['rental_income_monthly', 'Rental Income (Monthly)'],
                  ['other_income_annual', 'Other Income (Annual)'],
                  ['employee_epf_contribution_monthly', 'Employee EPF (Monthly)'],
                  ['employer_epf_contribution_monthly', 'Employer EPF (Monthly)'],
                ] as const
              ).map(([key, label]) => (
                <Field key={key} label={label}>
                  <NumInput
                    value={profile.income[key]}
                    onChange={(v) => setProfile((p) => ({ ...p, income: { ...p.income, [key]: v } }))}
                  />
                </Field>
              ))}
            </div>
          )}

          {step === 2 && (
            <div className="grid gap-4 md:grid-cols-2">
              {(
                [
                  ['monthly_living', 'Monthly Living'],
                  ['travel_monthly', 'Travel'],
                  ['medical_monthly', 'Medical'],
                  ['education_monthly', 'Education'],
                  ['insurance_premium_monthly', 'Insurance Premiums'],
                  ['entertainment_monthly', 'Entertainment'],
                  ['miscellaneous_monthly', 'Miscellaneous'],
                  ['rent_monthly', 'Rent'],
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
          )}

          {step === 3 && (
            <div className="space-y-4">
              {profile.loans.map((loan, idx) => (
                <div key={idx} className="grid gap-3 md:grid-cols-3 border border-border/60 rounded-xl p-4">
                  <Field label="Name">
                    <Input
                      value={loan.name}
                      onChange={(e) => {
                        const loans = [...profile.loans]
                        loans[idx] = { ...loan, name: e.target.value }
                        setProfile((p) => ({ ...p, loans }))
                      }}
                    />
                  </Field>
                  <Field label="Type">
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
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </Field>
                  {(
                    [
                      ['principal_outstanding', 'Outstanding'],
                      ['interest_rate_annual', 'Interest Rate (e.g. 0.085)'],
                      ['emi', 'EMI'],
                      ['tenure_months_remaining', 'Months Remaining'],
                      ['prepayment_amount', 'Prepayment'],
                    ] as const
                  ).map(([key, label]) => (
                    <Field key={key} label={label}>
                      <NumInput
                        step={key === 'interest_rate_annual' ? 0.001 : 1}
                        value={loan[key] as number}
                        onChange={(v) => {
                          const loans = [...profile.loans]
                          loans[idx] = { ...loan, [key]: v }
                          setProfile((p) => ({ ...p, loans }))
                        }}
                      />
                    </Field>
                  ))}
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
                        interest_rate_annual: 0.1,
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
          )}

          {step === 4 && (
            <div className="grid gap-4 md:grid-cols-2">
              {(Object.keys(profile.assets) as Array<keyof ClientProfile['assets']>).map((key) => (
                <Field key={key} label={key.replace(/_/g, ' ').toUpperCase()}>
                  <NumInput
                    value={profile.assets[key]}
                    onChange={(v) => setProfile((p) => ({ ...p, assets: { ...p.assets, [key]: v } }))}
                  />
                </Field>
              ))}
            </div>
          )}

          {step === 5 && (
            <div className="grid gap-4 md:grid-cols-2">
              {(Object.keys(profile.insurance) as Array<keyof ClientProfile['insurance']>).map((key) => (
                <Field key={key} label={key.replace(/_/g, ' ')}>
                  <NumInput
                    value={profile.insurance[key]}
                    onChange={(v) =>
                      setProfile((p) => ({ ...p, insurance: { ...p.insurance, [key]: v } }))
                    }
                  />
                </Field>
              ))}
            </div>
          )}

          {step === 6 && (
            <div className="space-y-4">
              {profile.investments.map((inv, idx) => (
                <div key={idx} className="grid gap-3 md:grid-cols-3 border border-border/60 rounded-xl p-4">
                  <Field label="Name">
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
                  {(
                    [
                      ['amount', 'Amount'],
                      ['monthly_sip', 'Monthly SIP'],
                      ['expected_return', 'Expected Return (e.g. 0.12)'],
                    ] as const
                  ).map(([key, label]) => (
                    <Field key={key} label={label}>
                      <NumInput
                        step={key === 'expected_return' ? 0.01 : 1}
                        value={inv[key] as number}
                        onChange={(v) => {
                          const investments = [...profile.investments]
                          investments[idx] = { ...inv, [key]: v }
                          setProfile((p) => ({ ...p, investments }))
                        }}
                      />
                    </Field>
                  ))}
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
                        expected_return: 0.12,
                        is_lumpsum: false,
                      } satisfies Investment,
                    ],
                  }))
                }
              >
                <Plus className="h-4 w-4" /> Add Investment
              </Button>
            </div>
          )}

          {step === 7 && (
            <div className="space-y-4">
              {profile.goals.map((goal, idx) => (
                <div key={idx} className="grid gap-3 md:grid-cols-3 border border-border/60 rounded-xl p-4">
                  <Field label="Name">
                    <Input
                      value={goal.name}
                      onChange={(e) => {
                        const goals = [...profile.goals]
                        goals[idx] = { ...goal, name: e.target.value }
                        setProfile((p) => ({ ...p, goals }))
                      }}
                    />
                  </Field>
                  <Field label="Type">
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
                        'house',
                        'car',
                        'children_education',
                        'children_marriage',
                        'retirement',
                        'vacation',
                        'emergency',
                        'business',
                        'custom',
                      ].map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
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
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Current Cost">
                    <NumInput
                      value={goal.current_cost}
                      onChange={(v) => {
                        const goals = [...profile.goals]
                        goals[idx] = { ...goal, current_cost: v }
                        setProfile((p) => ({ ...p, goals }))
                      }}
                    />
                  </Field>
                  <Field label="Target Year / Age">
                    <NumInput
                      value={goal.target_year}
                      onChange={(v) => {
                        const goals = [...profile.goals]
                        goals[idx] = { ...goal, target_year: v }
                        setProfile((p) => ({ ...p, goals }))
                      }}
                    />
                  </Field>
                  <Field label="Already Saved">
                    <NumInput
                      value={goal.already_saved}
                      onChange={(v) => {
                        const goals = [...profile.goals]
                        goals[idx] = { ...goal, already_saved: v }
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
                        target_year: p.personal.age + 5,
                        priority: 'medium',
                        already_saved: 0,
                        notes: '',
                      } satisfies Goal,
                    ],
                  }))
                }
              >
                <Plus className="h-4 w-4" /> Add Goal
              </Button>
            </div>
          )}

          {step === 8 && (
            <div className="grid gap-4 md:grid-cols-2">
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
                  ['hra_received_annual', 'HRA Received (Annual)'],
                  ['rent_paid_annual', 'Rent Paid (Annual)'],
                  ['section_80c_investments', 'Section 80C'],
                  ['section_80ccd_1b', 'Section 80CCD(1B)'],
                  ['section_80d_self', 'Section 80D Self'],
                  ['section_80d_parents', 'Section 80D Parents'],
                  ['home_loan_interest', 'Home Loan Interest'],
                  ['ltcg_equity', 'LTCG Equity'],
                  ['stcg_equity', 'STCG Equity'],
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
          )}

          {step === 9 && (
            <div className="space-y-4">
              <Field label="Manual Risk Profile">
                <select
                  className="h-10 w-full max-w-xs rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                  value={profile.risk_profile}
                  onChange={(e) => setProfile((p) => ({ ...p, risk_profile: e.target.value }))}
                >
                  {['conservative', 'moderate', 'aggressive'].map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </Field>
              {questionnaire && (
                <div className="space-y-4">
                  <p className="text-sm text-muted">Or complete the risk questionnaire:</p>
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
                          <option key={o.id} value={o.id}>
                            {o.text}
                          </option>
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
                  <p className="mt-2 text-muted">{String(riskResult.description)}</p>
                </div>
              )}
            </div>
          )}

          {step === 10 && (
            <div className="grid gap-4 md:grid-cols-2">
              {(
                [
                  ['general_inflation', 'General Inflation (e.g. 0.06)'],
                  ['healthcare_inflation', 'Healthcare Inflation'],
                  ['expected_equity_return', 'Expected Equity Return'],
                  ['expected_debt_return', 'Expected Debt Return'],
                  ['safe_withdrawal_rate', 'Safe Withdrawal Rate'],
                  ['salary_growth_rate', 'Salary Growth Rate'],
                ] as const
              ).map(([key, label]) => (
                <Field key={key} label={label}>
                  <NumInput
                    step={0.001}
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
              <p className="md:col-span-2 text-xs text-muted">
                Leave at 0 to use system defaults from config/assumptions.json.
              </p>
            </div>
          )}

          {step === 11 && (
            <div className="space-y-4">
              <p className="text-sm text-muted">
                One-click generation produces dashboard metrics, Excel workbook, PDF plan, charts, and
                recommendations.
              </p>
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
              {message && <p className="text-sm text-teal">{message}</p>}
              {preview && (
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  {[
                    ['Net Worth', formatINR(Number((preview.summary as Record<string, unknown>)?.net_worth || 0))],
                    [
                      'Health Score',
                      String((preview.health_score as Record<string, unknown>)?.score ?? '—'),
                    ],
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
                      <div className="mt-1 text-lg font-semibold">{v}</div>
                    </div>
                  ))}
                </div>
              )}
              {reportMeta.client_id && (
                <div className="flex flex-wrap gap-3">
                  <Button
                    variant="accent"
                    onClick={async () => {
                      const token = localStorage.getItem('access_token')
                      const res = await fetch(
                        `/api/v1/planning/download/excel/${reportMeta.client_id}`,
                        { headers: { Authorization: `Bearer ${token}` } },
                      )
                      const blob = await res.blob()
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'Financial_Plan.xlsx'
                      a.click()
                      URL.revokeObjectURL(url)
                    }}
                  >
                    <Download className="h-4 w-4" /> Download Excel
                  </Button>
                  <Button
                    variant="accent"
                    onClick={async () => {
                      const token = localStorage.getItem('access_token')
                      const res = await fetch(
                        `/api/v1/planning/download/pdf/${reportMeta.client_id}`,
                        { headers: { Authorization: `Bearer ${token}` } },
                      )
                      const blob = await res.blob()
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = 'Financial_Plan.pdf'
                      a.click()
                      URL.revokeObjectURL(url)
                    }}
                  >
                    <Download className="h-4 w-4" /> Download PDF
                  </Button>
                </div>
              )}
            </div>
          )}

          <div className="flex justify-between pt-4 border-t border-border/50">
            <Button variant="outline" disabled={step === 0} onClick={() => setStep((s) => s - 1)}>
              Back
            </Button>
            <Button disabled={step === STEPS.length - 1} onClick={() => setStep((s) => s + 1)}>
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
