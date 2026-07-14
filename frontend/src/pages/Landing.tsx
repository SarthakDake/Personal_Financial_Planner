import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ArrowRight, BarChart3, FileText, Shield } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-mesh relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -right-24 top-10 h-[28rem] w-[28rem] rounded-full bg-teal/10 blur-3xl animate-fade-in" />
        <div className="absolute -left-16 bottom-0 h-[22rem] w-[22rem] rounded-full bg-accent/10 blur-3xl animate-fade-in delay-2" />
      </div>

      <header className="relative mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy text-accent font-display text-2xl">
            W
          </div>
          <span className="font-display text-2xl text-navy dark:text-white">WealthCraft</span>
        </div>
        <Link to="/login">
          <Button variant="outline">Advisor Login</Button>
        </Link>
      </header>

      <section className="relative mx-auto grid max-w-6xl gap-10 px-6 pb-20 pt-10 md:grid-cols-[1.1fr_0.9fr] md:items-center md:pt-16">
        <div className="animate-fade-up">
          <h1 className="font-display text-5xl leading-[1.05] text-navy dark:text-white md:text-6xl">
            WealthCraft
          </h1>
          <p className="mt-5 max-w-xl text-lg text-slate-600 dark:text-slate-300">
            Enterprise financial planning for every client — configurable inputs, institutional
            calculations, and one-click Excel & PDF deliverables.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/login">
              <Button size="lg" className="animate-fade-up delay-1">
                Open Workspace <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a href="/docs" target="_blank" rel="noreferrer">
              <Button size="lg" variant="outline" className="animate-fade-up delay-2">
                API Docs
              </Button>
            </a>
          </div>
        </div>

        <div className="animate-fade-up delay-2 relative min-h-[280px] rounded-3xl border border-border/60 bg-navy p-8 text-white shadow-xl">
          <div className="font-display text-3xl">Clarity. Discipline. Prosperity.</div>
          <div className="mt-8 grid gap-4">
            {[
              { icon: BarChart3, text: 'Net worth, goals, retirement & Monte Carlo' },
              { icon: FileText, text: 'Consulting-grade Excel & 30–50 page PDF plans' },
              { icon: Shield, text: 'JWT auth, multi-client, zero hardcoded data' },
            ].map((item) => (
              <div key={item.text} className="flex items-start gap-3 text-sm text-slate-200">
                <item.icon className="mt-0.5 h-5 w-5 text-accent" />
                <span>{item.text}</span>
              </div>
            ))}
          </div>
          <div className="absolute bottom-0 right-0 h-24 w-40 bg-gradient-to-tl from-accent/30 to-transparent rounded-tl-[4rem]" />
        </div>
      </section>
    </div>
  )
}
