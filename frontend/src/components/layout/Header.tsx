import { useLocation } from 'react-router-dom'
import { Bell, Zap } from 'lucide-react'
import { UserMenu } from '@/components/auth/UserMenu'

const PAGE_TITLES: Record<string, string> = {
  '/': 'AI Tutor Chat',
  '/dashboard': 'Dashboard',
  '/create': 'Create New Video',
  '/history': 'Generation History',
}

export function Header() {
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] ?? 'AetherLearn.ai Platform'

  return (
    <header className="h-14 border-b border-white/10 bg-black/10 backdrop-blur-md flex items-center justify-between px-6 shrink-0">
      <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 glass rounded-full px-3 py-1.5">
          <Zap className="w-3.5 h-3.5 text-yellow-400" />
          <span className="text-xs font-medium text-muted-foreground">AI Engine</span>
        </div>
        <button className="w-8 h-8 rounded-full glass flex items-center justify-center hover:bg-white/10 transition-colors">
          <Bell className="w-4 h-4 text-muted-foreground" />
        </button>
        <UserMenu />
      </div>
    </header>
  )
}
