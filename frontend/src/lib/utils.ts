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
    case 'completed': return 'text-green-400'
    case 'running': return 'text-blue-400'
    case 'pending': return 'text-yellow-400'
    case 'failed': return 'text-red-400'
    default: return 'text-muted-foreground'
  }
}

export function getStatusBg(status: string): string {
  switch (status) {
    case 'completed': return 'bg-green-500/20 border-green-500/30 text-green-300'
    case 'running': return 'bg-blue-500/20 border-blue-500/30 text-blue-300'
    case 'pending': return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-300'
    case 'failed': return 'bg-red-500/20 border-red-500/30 text-red-300'
    default: return 'bg-muted/20 border-border text-muted-foreground'
  }
}
