import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  BookOpen,
  LayoutDashboard,
  Users,
  FileSpreadsheet,
  SlidersHorizontal,
  Moon,
  Sun,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { logout, me } from '@/lib/api'
import { cn } from '@/lib/utils'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/clients', label: 'Clients', icon: Users },
  { to: '/planner', label: 'Planner', icon: FileSpreadsheet },
  { to: '/what-if', label: 'What-If', icon: SlidersHorizontal },
  { to: '/glossary', label: 'Glossary', icon: BookOpen },
]

export default function Layout() {
  const navigate = useNavigate()
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark')
  const [userName, setUserName] = useState('Advisor')
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  useEffect(() => {
    me()
      .then((u) => setUserName(u.full_name || u.email))
      .catch(() => navigate('/login'))
  }, [navigate])

  return (
    <div className="min-h-screen bg-mesh pb-20 md:pb-0">
      <header className="sticky top-0 z-40 border-b border-border/70 dark:border-border-dark bg-white/80 dark:bg-surface-dark/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 md:px-6">
          <Link to="/dashboard" className="flex items-center gap-2.5 animate-fade-in min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-navy text-accent font-display text-xl">
              W
            </div>
            <div className="min-w-0">
              <div className="font-display text-lg sm:text-xl leading-none text-navy dark:text-white truncate">
                WealthCraft
              </div>
              <div className="hidden sm:block text-[11px] tracking-wide text-muted">
                Professional Financial Planner
              </div>
            </div>
          </Link>

          <nav className="hidden lg:flex items-center gap-1">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
                    isActive
                      ? 'bg-navy text-white'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-surface dark:hover:bg-card-dark',
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-1.5 sm:gap-2">
            <span className="hidden md:inline text-xs text-muted max-w-[120px] truncate">{userName}</span>
            <Button variant="ghost" size="icon" onClick={() => setDark((d) => !d)} aria-label="Toggle theme">
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="hidden sm:inline-flex"
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setMenuOpen((o) => !o)}
              aria-label="Menu"
            >
              {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {menuOpen && (
          <div className="lg:hidden border-t border-border/60 bg-white/95 dark:bg-surface-dark/95 px-4 py-3 space-y-1 animate-fade-in">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm',
                    isActive ? 'bg-navy text-white' : 'text-slate-700 dark:text-slate-200',
                  )
                }
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            ))}
            <button
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-danger"
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-5 md:px-6 md:py-8">
        <Outlet />
      </main>

      {/* Mobile bottom navigation */}
      <nav className="fixed bottom-0 inset-x-0 z-40 border-t border-border/70 dark:border-border-dark bg-white/95 dark:bg-surface-dark/95 backdrop-blur md:hidden">
        <div className="grid grid-cols-5 gap-0.5 px-1 py-1.5">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-0.5 rounded-lg py-1.5 text-[10px]',
                  isActive ? 'text-navy dark:text-accent font-semibold' : 'text-muted',
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
