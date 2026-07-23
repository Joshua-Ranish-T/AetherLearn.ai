import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  PlusCircle,
  History,
  Settings,
  Video,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/create', icon: PlusCircle, label: 'Create Video' },
  { to: '/history', icon: History, label: 'History' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -80, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-64 shrink-0 flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-xl"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-white/10">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-purple-hot flex items-center justify-center shadow-lg shadow-primary/30">
          <Video className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-bold gradient-text">EduVideo</h1>
          <p className="text-xs text-muted-foreground">AI Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={cn('w-4 h-4', isActive && 'text-primary')} />
                {label}
                {isActive && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-primary"
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom badge */}
      <div className="p-4 border-t border-white/10">
        <div className="glass rounded-lg p-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          <div>
            <p className="text-xs font-medium">Powered by Gemini</p>
            <p className="text-xs text-muted-foreground">AI Multi-Agent</p>
          </div>
        </div>
      </div>
    </motion.aside>
  )
}
