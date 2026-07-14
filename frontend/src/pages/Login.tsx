import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login, register } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('advisor@wealthcraft.example')
  const [password, setPassword] = useState('Advisor@123')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'register') {
        await register(email, password, fullName)
      }
      await login(email, password)
      navigate('/dashboard')
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Authentication failed'
      setError(String(message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center px-4">
      <div className="w-full max-w-md animate-fade-up">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-navy text-accent font-display text-3xl">
            W
          </div>
          <h1 className="font-display text-4xl text-navy dark:text-white">WealthCraft</h1>
          <p className="mt-2 text-sm text-muted">Clarity. Discipline. Prosperity.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>{mode === 'login' ? 'Advisor Sign In' : 'Create Advisor Account'}</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={onSubmit}>
              {mode === 'register' && (
                <div className="space-y-1.5">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
                </div>
              )}
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>
              {error && <p className="text-sm text-danger">{error}</p>}
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Register & Sign In'}
              </Button>
            </form>
            <p className="mt-4 text-center text-sm text-muted">
              {mode === 'login' ? (
                <>
                  New advisor?{' '}
                  <button className="text-teal underline" onClick={() => setMode('register')}>
                    Create account
                  </button>
                </>
              ) : (
                <>
                  Already registered?{' '}
                  <button className="text-teal underline" onClick={() => setMode('login')}>
                    Sign in
                  </button>
                </>
              )}
            </p>
            <p className="mt-3 text-center text-xs text-muted">
              Demo: advisor@wealthcraft.example / Advisor@123
            </p>
            <p className="mt-2 text-center text-xs">
              <Link to="/" className="text-teal">
                Back
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
