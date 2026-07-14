import axios from 'axios'
import type { Client, ClientProfile, PlanResult } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function login(email: string, password: string) {
  const { data } = await api.post('/auth/login', { email, password })
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  return data
}

export async function register(email: string, password: string, full_name: string) {
  const { data } = await api.post('/auth/register', { email, password, full_name })
  return data
}

export async function me() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function listClients(): Promise<Client[]> {
  const { data } = await api.get('/clients')
  return data
}

export async function createClient(profile: ClientProfile, notes = '') {
  const { data } = await api.post('/clients', { profile, notes })
  return data as Client
}

export async function updateClient(id: string, profile: ClientProfile, notes?: string) {
  const { data } = await api.put(`/clients/${id}`, { profile, notes })
  return data as Client
}

export async function getClient(id: string): Promise<Client> {
  const { data } = await api.get(`/clients/${id}`)
  return data
}

export async function deleteClient(id: string) {
  await api.delete(`/clients/${id}`)
}

export async function previewPlan(profile: ClientProfile): Promise<PlanResult> {
  const { data } = await api.post('/planning/preview', profile)
  return data
}

export async function generatePlan(payload: {
  client_id?: string
  profile?: ClientProfile
  generate_excel?: boolean
  generate_pdf?: boolean
  generate_charts?: boolean
  save?: boolean
}) {
  const { data } = await api.post('/planning/generate', payload)
  return data as {
    id?: string
    client_id?: string
    plan: PlanResult
    excel_path?: string
    pdf_path?: string
    chart_paths: string[]
  }
}

export async function whatIf(
  profile: ClientProfile,
  adjustments: Record<string, number | null | undefined>,
): Promise<PlanResult> {
  const { data } = await api.post('/planning/what-if', { profile, ...adjustments })
  return data
}

export async function getRiskQuestionnaire() {
  const { data } = await api.get('/planning/risk-questionnaire')
  return data
}

export async function scoreRisk(answers: Record<string, string>) {
  const { data } = await api.post('/planning/risk-score', answers)
  return data
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export default api
