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
      whileHover={{ y: -2 }}
      className="glass rounded-xl p-5 border border-white/10 hover:border-white/20 transition-all"
    >
      <div className="flex items-center justify-between mb-3">
        <div className={cn('w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center', color)}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-3xl font-bold">{value}</span>
      </div>
      <p className="text-sm text-muted-foreground">{label}</p>
    </motion.div>
  )
}

function ProjectCard({ project, onDelete }: { project: Project; onDelete: (id: string) => void }) {
  const navigate = useNavigate()
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="glass-hover rounded-xl p-5 cursor-pointer"
      onClick={() => navigate(`/projects/${project.id}`)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{project.title}</h3>
          <p className="text-xs text-muted-foreground mt-0.5 truncate">{project.description || 'No description'}</p>
        </div>
        <span className={cn('ml-3 shrink-0 text-xs px-2 py-1 rounded-full border', getStatusBg(project.status))}>
          {project.status}
        </span>
      </div>
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <Clock className="w-3 h-3" />
          {formatRelativeTime(project.created_at)}
        </div>
        <div className="flex items-center gap-2">
          <span className="capitalize bg-white/10 rounded px-1.5 py-0.5">{project.input_type}</span>
          {project.status === 'completed' && (
            <button
              onClick={(e) => { e.stopPropagation(); navigate(`/projects/${project.id}`) }}
              className="flex items-center gap-1 text-primary hover:text-primary/80 transition-colors"
            >
              View <ArrowRight className="w-3 h-3" />
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
          <h1 className="text-2xl font-bold">
            Welcome to <span className="gradient-text">EduVideo</span>
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
        <h2 className="text-base font-semibold mb-4">Recent Projects</h2>
        {isLoading ? (
          <div className="grid grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass rounded-xl p-5 h-28 shimmer" />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div className="glass rounded-xl p-12 text-center">
            <Video className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-semibold mb-2">No projects yet</h3>
            <p className="text-sm text-muted-foreground mb-4">Create your first educational video</p>
            <button
              onClick={() => navigate('/create')}
              className="btn-glow bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium"
            >
              Create Project
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
