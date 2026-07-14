import { Link } from 'react-router-dom'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ArrowRight, BarChart3, FileText, Shield, TrendingUp } from 'lucide-react'

export default function Landing() {
  // Landing presents the investment dark aesthetic by default
  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])

  return (
    <div className="min-h-screen bg-mesh relative overflow-hidden dark">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -right-20 top-0 h-[30rem] w-[30rem] rounded-full bg-accent/20 blur-3xl animate-pulse-soft" />
        <div className="absolute -left-16 bottom-10 h-[22rem] w-[22rem] rounded-full bg-sky-400/10 blur-3xl" />
      </div>

      <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent text-white font-display text-2xl glow-blue">
            W
          </div>
          <span className="font-display text-2xl text-white">WealthCraft</span>
        </div>
        <Link to="/login">
          <Button variant="outline">Advisor Login</Button>
        </Link>
      </header>

      <section className="relative mx-auto grid max-w-6xl gap-10 px-6 pb-20 pt-10 md:grid-cols-[1.1fr_0.9fr] md:items-center md:pt-16">
        <div className="animate-fade-up">
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-400/10 px-3 py-1 text-xs text-sky-300 mb-4">
            <TrendingUp className="h-3.5 w-3.5" />
            Dark fintech workspace for advisors
          </div>
          <h1 className="font-display text-5xl leading-[1.05] text-white md:text-6xl">
            WealthCraft
          </h1>
          <p className="mt-5 max-w-xl text-lg text-slate-300">
            A sleek investment planning desk — portfolio insights, goal tracking, and one-click
            Excel & PDF plans with clear data visualization.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/login">
              <Button size="lg" className="animate-fade-up delay-1">
                Open Workspace <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
              <Button size="lg" variant="outline" className="animate-fade-up delay-2">
                API Docs
              </Button>
            </a>
          </div>
        </div>

        <div className="animate-fade-up delay-2 relative min-h-[300px] rounded-3xl border border-slate-700/80 bg-gradient-to-br from-slate-900 via-[#121a2b] to-blue-950 p-8 text-white glow-blue">
          <div className="font-display text-3xl text-sky-100">Clarity. Discipline. Prosperity.</div>
          <div className="mt-8 grid gap-4">
            {[
              { icon: BarChart3, text: 'Net worth, allocation & retirement progress at a glance' },
              { icon: FileText, text: 'Consulting-grade Excel & multi-page PDF plans' },
              { icon: Shield, text: 'JWT-secured multi-client workspace' },
            ].map((item) => (
              <div key={item.text} className="flex items-start gap-3 text-sm text-slate-200">
                <div className="rounded-lg bg-accent/20 p-1.5">
                  <item.icon className="h-4 w-4 text-sky-300" />
                </div>
                <span>{item.text}</span>
              </div>
            ))}
          </div>
          <div className="mt-8 grid grid-cols-3 gap-3 text-center">
            {[
              ['Net Worth', '₹2.3Cr'],
              ['Health', 'B+'],
              ['Goals', '7'],
            ].map(([k, v]) => (
              <div key={k} className="rounded-xl bg-slate-950/50 border border-slate-700/60 py-3">
                <div className="text-[10px] uppercase tracking-wider text-slate-400">{k}</div>
                <div className="mt-1 text-lg font-semibold text-sky-300">{v}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
