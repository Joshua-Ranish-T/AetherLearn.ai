import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, Video, Clock, CheckCircle2, XCircle, Loader2, ArrowRight } from 'lucide-react'
import { useProjects, useDeleteProject } from '@/hooks/useProjects'
import { cn, formatRelativeTime, getStatusBg } from '@/lib/utils'
import type { Project } from '@/types'

const STATS = [
  { label: 'Total Projects', key: 'total', color: 'from-blue-500 to-indigo-600', icon: Video },
  { label: 'Completed', key: 'completed', color: 'from-green-500 to-emerald-600', icon: CheckCircle2 },
  { label: 'In Progress', key: 'running', color: 'from-yellow-500 to-orange-600', icon: Loader2 },
  { label: 'Failed', key: 'failed', color: 'from-red-500 to-rose-600', icon: XCircle },
]

function StatCard({ label, value, color, icon: Icon }: { label: string; value: number; color: string; icon: React.ElementType }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="glass rounded-2xl p-5 hover:shadow-lg transition-all"
    >
      <div className="flex items-center justify-between mb-3">
        <div className={cn('w-11 h-11 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-md', color)}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-3xl font-black text-slate-800">{value}</span>
      </div>
      <p className="text-sm font-semibold text-slate-500">{label}</p>
    </motion.div>
  )
}

function ProjectCard({ project, onDelete }: { project: Project; onDelete: (id: string) => void }) {
  const navigate = useNavigate()
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="glass-hover rounded-2xl p-5 cursor-pointer group"
      onClick={() => navigate(`/projects/${project.id}`)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-slate-800 truncate group-hover:text-[#1BC237] transition-colors">{project.title}</h3>
          <p className="text-xs text-slate-500 mt-1 truncate font-medium">{project.description || 'No description provided'}</p>
        </div>
        <span className={cn('ml-3 shrink-0 text-xs px-2.5 py-1 rounded-full border shadow-sm', getStatusBg(project.status))}>
          {project.status}
        </span>
      </div>
      <div className="flex items-center justify-between text-xs font-medium text-slate-400 mt-4 pt-3 border-t border-slate-100">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          {formatRelativeTime(project.created_at)}
        </div>
        <div className="flex items-center gap-2">
          <span className="capitalize bg-slate-100 text-slate-600 rounded-md px-2 py-0.5 font-semibold border border-slate-200/60">{project.input_type}</span>
          {project.status === 'completed' && (
            <button
              onClick={(e) => { e.stopPropagation(); navigate(`/projects/${project.id}`) }}
              className="flex items-center gap-1 text-[#1BC237] font-bold hover:underline transition-all"
            >
              View <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading } = useProjects(50)
  const deleteProject = useDeleteProject()

  const projects = data?.items ?? []
  const stats = {
    total: projects.length,
    completed: projects.filter(p => p.status === 'completed').length,
    running: projects.filter(p => p.status === 'running' || p.status === 'pending').length,
    failed: projects.filter(p => p.status === 'failed').length,
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-baseline gap-1.5">
            <span>Welcome to</span>
            <span className="flex items-baseline tracking-tight">
              <span className="text-slate-900 dark:text-white font-black">Aether</span>
              <span className="text-[#1BC237] font-black">Learn</span>
              <span className="text-slate-400 font-light text-xl ml-0.5">.ai</span>
            </span>
          </h1>
          <p className="text-muted-foreground mt-1">Convert educational content into animated videos with AI</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => navigate('/create')}
          className="btn-glow flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-5 py-2.5 rounded-xl font-medium text-sm shadow-lg shadow-primary/25 transition-all"
        >
          <PlusCircle className="w-4 h-4" />
          New Video
        </motion.button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {STATS.map(({ label, key, color, icon }) => (
          <StatCard key={key} label={label} value={stats[key as keyof typeof stats]} color={color} icon={icon} />
        ))}
      </div>

      {/* Projects */}
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-4">Recent Projects</h2>
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass rounded-2xl p-5 h-32 shimmer" />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="glass rounded-2xl p-12 text-center border border-slate-200/80 shadow-sm bg-white/80">
            <div className="w-16 h-16 rounded-2xl bg-green-50 border border-green-200/60 flex items-center justify-center mx-auto mb-4 shadow-sm">
              <Video className="w-8 h-8 text-[#1BC237]" />
            </div>
            <h3 className="font-bold text-slate-800 text-lg mb-1">No projects yet</h3>
            <p className="text-sm text-slate-500 mb-6 max-w-sm mx-auto">Create your first AI-generated 3D animated educational video in just seconds.</p>
            <button
              onClick={() => navigate('/create')}
              className="btn-glow bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-xl text-sm font-semibold shadow-lg shadow-primary/25 transition-all"
            >
              Create Your First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.slice(0, 9).map((project, i) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <ProjectCard project={project} onDelete={(id) => deleteProject.mutate(id)} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
