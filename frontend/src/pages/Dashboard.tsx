import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { listClients, previewPlan, seedDemoClient } from '@/lib/api'
import type { Client, PlanResult } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatINR, formatPct } from '@/lib/utils'
import { BookOpen, Plus, RefreshCw, Sparkles } from 'lucide-react'

const COLORS = ['#1c1917', '#57534e', '#a89078', '#78716c', '#926f4c']

export default function Dashboard() {
  const [clients, setClients] = useState<Client[]>([])
  const [selected, setSelected] = useState<string>('')
  const [plan, setPlan] = useState<PlanResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')

  async function refreshClients(preferId?: string) {
    const c = await listClients()
    setClients(c)
    const next = preferId || selected || c[0]?.id || ''
    setSelected(next)
  }

  useEffect(() => {
    refreshClients().catch(() => undefined)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!selected) {
      setPlan(null)
      return
    }
    const client = clients.find((c) => c.id === selected)
    if (!client) return
    setLoading(true)
    previewPlan(client.profile_data)
      .then(setPlan)
      .finally(() => setLoading(false))
  }, [selected, clients])

  const summary = plan?.summary
  const allocation = Object.entries(
    (plan?.portfolio as { current?: { asset_class?: Record<string, number> } })?.current
      ?.asset_class || {},
  )
    .filter(([, v]) => Number(v) > 0)
    .map(([name, value]) => ({ name: name.replace(/_/g, ' '), value: Number(value) }))

  const goals = (plan?.goals || []).map((g) => ({
    name: String(g.name).slice(0, 14),
    progress: Number(g.progress_percent || 0),
  }))

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end sm:justify-between animate-fade-up">
        <div>
          <h1 className="font-display text-3xl sm:text-4xl text-navy dark:text-white">Dashboard</h1>
          <p className="mt-1 text-sm text-muted">Live financial snapshot for the selected client.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            className="h-10 min-w-0 flex-1 sm:flex-none sm:min-w-[200px] rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
          >
            {clients.length === 0 && <option value="">No clients yet</option>}
            {clients.map((c) => (
              <option key={c.id} value={c.id}>
                {c.full_name}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              const r = await seedDemoClient()
              setMsg(`Demo ${r.action}: ${r.full_name}`)
              await refreshClients(r.id)
            }}
          >
            <Sparkles className="h-4 w-4" /> Load Demo
          </Button>
          <Link to="/planner">
            <Button size="sm">
              <Plus className="h-4 w-4" /> New Plan
            </Button>
          </Link>
          <Link to="/glossary" className="hidden sm:block">
            <Button size="sm" variant="ghost">
              <BookOpen className="h-4 w-4" /> Terms
            </Button>
          </Link>
        </div>
      </div>

      {msg && <p className="text-sm text-stone-600 dark:text-stone-300 animate-fade-in">{msg}</p>}

      {!clients.length && (
        <Card className="animate-fade-up">
          <CardContent className="py-10 text-center space-y-4">
            <p className="text-muted">Create a client or load the real-life demo family to explore.</p>
            <div className="flex flex-wrap justify-center gap-2">
              <Button
                onClick={async () => {
                  const r = await seedDemoClient()
                  await refreshClients(r.id)
                }}
              >
                <Sparkles className="h-4 w-4" /> Load Demo Family
              </Button>
              <Link to="/planner">
                <Button variant="outline">Start Blank Planner</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted animate-fade-in">
          <RefreshCw className="h-4 w-4 animate-spin" /> Calculating plan…
        </div>
      )}

      {plan && summary && (
        <>
          <div className="grid gap-3 grid-cols-2 lg:grid-cols-4">
            {[
              { label: 'Net Worth', value: formatINR(Number(summary.net_worth || 0)) },
              { label: 'Monthly Surplus', value: formatINR(Number(summary.monthly_surplus || 0)) },
              {
                label: 'Health Score',
                value: `${summary.health_score} (${summary.health_grade})`,
              },
              {
                label: 'Retirement Progress',
                value: formatPct(Number(summary.retirement_progress_percent || 0)),
              },
            ].map((kpi, i) => (
              <Card key={kpi.label} className={`animate-fade-up delay-${i + 1}`}>
                <CardHeader className="p-4 pb-1">
                  <CardTitle className="text-[10px] sm:text-xs uppercase tracking-wider text-muted font-medium">
                    {kpi.label}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4 pt-1">
                  <div className="text-lg sm:text-2xl font-semibold text-navy dark:text-white break-words">
                    {kpi.value}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card className="animate-fade-up">
              <CardHeader>
                <CardTitle>Asset Allocation</CardTitle>
              </CardHeader>
              <CardContent className="h-64 sm:h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={allocation} dataKey="value" nameKey="name" innerRadius={45} outerRadius={80}>
                      {allocation.map((_, idx) => (
                        <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => formatINR(Number(v))} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="animate-fade-up delay-1">
              <CardHeader>
                <CardTitle>Goal Progress</CardTitle>
              </CardHeader>
              <CardContent className="h-64 sm:h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={goals} layout="vertical" margin={{ left: 8, right: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 10 }} />
                    <YAxis type="category" dataKey="name" width={70} tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Bar dataKey="progress" fill="#57534e" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Loans</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                {(plan.loans || []).length === 0 && <p className="text-muted">No loans</p>}
                {(plan.loans || []).map((l) => (
                  <div key={String(l.name)} className="flex justify-between gap-2 border-b border-border/50 py-2">
                    <span className="truncate">{String(l.name)}</span>
                    <span className="shrink-0">{formatINR(Number(l.principal_outstanding))}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Tax</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <div className="flex justify-between gap-2">
                  <span>Recommended</span>
                  <span className="font-medium uppercase">{String(plan.tax.recommended_regime)}</span>
                </div>
                <div className="flex justify-between gap-2">
                  <span>Savings vs other</span>
                  <span>{formatINR(Number(plan.tax.tax_savings_by_switching || 0))}</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Insurance</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                {['life', 'health'].map((key) => {
                  const d = (plan.insurance as Record<string, { adequate?: boolean; gap?: number }>)[key]
                  return (
                    <div key={key} className="flex justify-between gap-2">
                      <span className="capitalize">{key}</span>
                      <span className={d?.adequate ? 'text-accent' : 'text-warm'}>
                        {d?.adequate ? 'Adequate' : `Gap ${formatINR(Number(d?.gap || 0))}`}
                      </span>
                    </div>
                  )
                })}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
