import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatINR(value: number, decimals = 0): string {
  const abs = Math.abs(value)
  const formatted = new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  }).format(abs)
  return `${value < 0 ? '-' : ''}₹${formatted}`
}

export function formatPct(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}
