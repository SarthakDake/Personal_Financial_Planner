import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteClient, listClients } from '@/lib/api'
import type { Client } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Plus, Trash2, Pencil } from 'lucide-react'

export default function Clients() {
  const [clients, setClients] = useState<Client[]>([])

  async function refresh() {
    setClients(await listClients())
  }

  useEffect(() => {
    refresh()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between animate-fade-up">
        <div>
          <h1 className="font-display text-4xl text-navy dark:text-white">Clients</h1>
          <p className="mt-1 text-sm text-muted">Manage configurable client profiles — no hardcoded data.</p>
        </div>
        <Link to="/planner">
          <Button>
            <Plus className="h-4 w-4" /> Add Client
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {clients.map((c, i) => (
          <Card key={c.id} className={`animate-fade-up delay-${(i % 3) + 1}`}>
            <CardHeader className="flex flex-row items-start justify-between gap-2">
              <div>
                <CardTitle>{c.full_name}</CardTitle>
                <p className="text-xs text-muted mt-1">
                  {c.email || 'No email'} · Risk: {c.risk_profile}
                </p>
              </div>
              <div className="flex gap-1">
                <Link to={`/planner?client=${c.id}`}>
                  <Button size="icon" variant="ghost">
                    <Pencil className="h-4 w-4" />
                  </Button>
                </Link>
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={async () => {
                    if (confirm('Deactivate this client?')) {
                      await deleteClient(c.id)
                      refresh()
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4 text-danger" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="text-sm text-muted">
              Phone: {c.phone || '—'} · Updated {new Date(c.updated_at).toLocaleDateString()}
            </CardContent>
          </Card>
        ))}
        {!clients.length && (
          <Card>
            <CardContent className="py-10 text-center text-muted">No clients yet.</CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
