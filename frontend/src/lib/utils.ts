import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60_000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'completed': return 'text-green-700 font-semibold'
    case 'running': return 'text-blue-700 font-semibold'
    case 'pending': return 'text-amber-700 font-semibold'
    case 'failed': return 'text-red-700 font-semibold'
    default: return 'text-slate-600 font-semibold'
  }
}

export function getStatusBg(status: string): string {
  switch (status) {
    case 'completed': return 'bg-green-50 border-green-200 text-green-700 font-semibold'
    case 'running': return 'bg-blue-50 border-blue-200 text-blue-700 font-semibold'
    case 'pending': return 'bg-amber-50 border-amber-200 text-amber-700 font-semibold'
    case 'failed': return 'bg-red-50 border-red-200 text-red-700 font-semibold'
    default: return 'bg-slate-50 border-slate-200 text-slate-600 font-semibold'
  }
}
