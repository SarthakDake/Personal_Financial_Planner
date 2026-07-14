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
import { listClients, previewPlan } from '@/lib/api'
import type { Client, PlanResult } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatINR, formatPct } from '@/lib/utils'
import { Plus, RefreshCw } from 'lucide-react'

const COLORS = ['#0B3D5C', '#1F6F8B', '#99C24D', '#F18F01', '#C73E1D']

export default function Dashboard() {
  const [clients, setClients] = useState<Client[]>([])
  const [selected, setSelected] = useState<string>('')
  const [plan, setPlan] = useState<PlanResult | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    listClients().then((c) => {
      setClients(c)
      if (c[0]) setSelected(c[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selected) return
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
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4 animate-fade-up">
        <div>
          <h1 className="font-display text-4xl text-navy dark:text-white">Dashboard</h1>
          <p className="mt-1 text-sm text-muted">Live financial snapshot for the selected client.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            className="h-10 rounded-lg border border-border dark:border-border-dark bg-white dark:bg-card-dark px-3 text-sm"
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
          <Link to="/planner">
            <Button>
              <Plus className="h-4 w-4" /> New Plan
            </Button>
          </Link>
        </div>
      </div>

      {!clients.length && (
        <Card className="animate-fade-up">
          <CardContent className="py-10 text-center">
            <p className="text-muted mb-4">Create a client profile to see the dashboard.</p>
            <Link to="/planner">
              <Button>Start Client Planner</Button>
            </Link>
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
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                <CardHeader>
                  <CardTitle className="text-xs uppercase tracking-wider text-muted font-medium">
                    {kpi.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-semibold text-navy dark:text-white">{kpi.value}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card className="animate-fade-up">
              <CardHeader>
                <CardTitle>Asset Allocation</CardTitle>
              </CardHeader>
              <CardContent className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={allocation} dataKey="value" nameKey="name" innerRadius={55} outerRadius={95}>
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
              <CardContent className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={goals} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis type="category" dataKey="name" width={90} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="progress" fill="#1F6F8B" radius={[0, 6, 6, 0]} />
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
                  <div key={String(l.name)} className="flex justify-between border-b border-border/50 py-2">
                    <span>{String(l.name)}</span>
                    <span>{formatINR(Number(l.principal_outstanding))}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Tax</CardTitle>
              </CardHeader>
              <CardContent className="text-sm space-y-2">
                <div className="flex justify-between">
                  <span>Recommended</span>
                  <span className="font-medium uppercase">{String(plan.tax.recommended_regime)}</span>
                </div>
                <div className="flex justify-between">
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
                    <div key={key} className="flex justify-between">
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
