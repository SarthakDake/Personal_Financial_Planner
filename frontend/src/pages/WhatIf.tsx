import { useEffect, useState, useTransition } from 'react'
import { listClients, whatIf } from '@/lib/api'
import type { Client, PlanResult } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { formatINR, formatPct } from '@/lib/utils'

export default function WhatIf() {
  const [clients, setClients] = useState<Client[]>([])
  const [selected, setSelected] = useState('')
  const [plan, setPlan] = useState<PlanResult | null>(null)
  const [isPending, startTransition] = useTransition()
  const [income, setIncome] = useState(0)
  const [expenses, setExpenses] = useState(0)
  const [sip, setSip] = useState(0)
  const [inflation, setInflation] = useState(6)
  const [returns, setReturns] = useState(12)
  const [loanRate, setLoanRate] = useState(0)
  const [retAge, setRetAge] = useState(60)

  useEffect(() => {
    listClients().then((c) => {
      setClients(c)
      if (c[0]) {
        setSelected(c[0].id)
        setRetAge(c[0].profile_data.personal.retirement_age)
      }
    })
  }, [])

  useEffect(() => {
    const client = clients.find((c) => c.id === selected)
    if (!client) return
    startTransition(() => {
      whatIf(client.profile_data, {
        income_change_percent: income,
        expense_change_percent: expenses,
        sip_change_absolute: sip,
        inflation_override: inflation / 100,
        returns_override: returns / 100,
        loan_interest_change_percent: loanRate,
        retirement_age_override: retAge,
      }).then(setPlan)
    })
  }, [selected, clients, income, expenses, sip, inflation, returns, loanRate, retAge])

  const Slider = ({
    label,
    value,
    min,
    max,
    step,
    onChange,
    suffix = '',
  }: {
    label: string
    value: number
    min: number
    max: number
    step: number
    onChange: (v: number) => void
    suffix?: string
  }) => (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <Label>{label}</Label>
        <span className="text-muted">
          {value}
          {suffix}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-teal"
      />
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="animate-fade-up">
        <h1 className="font-display text-3xl sm:text-4xl text-navy dark:text-white">What-If Analysis</h1>
        <p className="mt-1 text-sm text-muted">
          Sliders use whole percentages (e.g. inflation 6 = 6%). SIP change is Monthly ₹.
          {isPending ? ' Updating…' : ''}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        <Card className="animate-fade-up h-fit">
          <CardHeader>
            <CardTitle>Controls</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div>
              <Label>Client</Label>
              <select
                className="mt-1 h-10 w-full rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.full_name}
                  </option>
                ))}
              </select>
            </div>
            <Slider label="Income change" value={income} min={-50} max={50} step={1} onChange={setIncome} suffix="%" />
            <Slider label="Expense change" value={expenses} min={-50} max={50} step={1} onChange={setExpenses} suffix="%" />
            <Slider label="Additional SIP (Monthly ₹)" value={sip} min={-50000} max={100000} step={1000} onChange={setSip} suffix=" ₹/mo" />
            <Slider label="Inflation (Annual %)" value={inflation} min={2} max={12} step={0.5} onChange={setInflation} suffix="%" />
            <Slider label="Expected returns (Annual %)" value={returns} min={4} max={18} step={0.5} onChange={setReturns} suffix="%" />
            <Slider label="Loan interest change (%)" value={loanRate} min={-30} max={30} step={1} onChange={setLoanRate} suffix="%" />
            <Slider label="Retirement age" value={retAge} min={45} max={70} step={1} onChange={setRetAge} />
          </CardContent>
        </Card>

        <div className="space-y-4 animate-fade-up delay-1">
          {plan && (
            <>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {[
                  ['Monthly Surplus', formatINR(Number(plan.cash_flow.monthly_surplus || 0))],
                  ['Net Worth', formatINR(Number(plan.net_worth.net_worth || 0))],
                  ['Health Score', String(plan.health_score.score)],
                  ['Required Corpus', formatINR(Number(plan.retirement.required_corpus || 0))],
                  ['Projected Corpus', formatINR(Number(plan.retirement.projected_corpus || 0))],
                  ['Retirement Progress', formatPct(Number(plan.retirement.progress_percent || 0))],
                ].map(([label, value]) => (
                  <Card key={label}>
                    <CardHeader>
                      <CardTitle className="text-xs uppercase tracking-wider text-muted">{label}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-xl font-semibold">{value}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              <Card>
                <CardHeader>
                  <CardTitle>Scenario Comparison</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {Object.entries(plan.scenarios || {}).map(([key, val]) => {
                    const v = val as Record<string, unknown>
                    return (
                      <div key={key} className="flex flex-wrap justify-between gap-2 border-b border-border/40 py-2">
                        <span className="font-medium">{String(v.label || key)}</span>
                        <span>
                          Shortfall {formatINR(Number(v.shortfall || 0))} · Progress{' '}
                          {formatPct(Number(v.progress_percent || 0))}
                        </span>
                      </div>
                    )
                  })}
                </CardContent>
              </Card>
            </>
          )}
          {!plan && !clients.length && (
            <Card>
              <CardContent className="py-10 text-center text-muted">
                Create a client first to run what-if analysis.
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
