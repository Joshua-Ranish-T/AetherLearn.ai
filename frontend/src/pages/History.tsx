import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Filter, Clock, Video as VideoIcon, CheckCircle2, XCircle, ChevronRight, Play } from 'lucide-react'
import { useProjects } from '@/hooks/useProjects'
import { formatRelativeTime, formatDuration, cn, getStatusBg } from '@/lib/utils'

export function History() {
  const navigate = useNavigate()
  const { data, isLoading } = useProjects(100)
  const [filter, setFilter] = useState<'all' | 'completed' | 'failed' | 'running'>('all')
  const [search, setSearch] = useState('')

  const projects = data?.items || []

  const filteredProjects = projects.filter(p => {
    if (filter !== 'all' && p.status !== filter) return false
    if (search && !p.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="max-w-6xl mx-auto animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Generation History</h1>
          <p className="text-muted-foreground mt-1">View all your past and current video projects</p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-white/10 focus:outline-none focus:border-primary/50 text-sm"
          />
        </div>
        <div className="flex items-center gap-2 glass rounded-xl p-1">
          {['all', 'completed', 'running', 'failed'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f as typeof filter)}
              className={cn(
                'px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all',
                filter === f ? 'bg-primary/20 text-primary' : 'hover:bg-white/5 text-muted-foreground'
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <div className="glass rounded-xl overflow-hidden border border-white/10">
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 bg-black/20 text-sm font-medium text-muted-foreground">
          <div className="col-span-4">Project Name</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2">Input Type</div>
          <div className="col-span-3">Created</div>
          <div className="col-span-1"></div>
        </div>

        {isLoading ? (
          <div className="divide-y divide-white/10">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="p-4 h-16 shimmer" />
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground">
            No projects found matching your criteria.
          </div>
        ) : (
          <div className="divide-y divide-white/10">
            {filteredProjects.map((project, i) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.05 }}
                className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-white/5 transition-colors cursor-pointer group"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <div className="col-span-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                    <VideoIcon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="font-medium text-sm truncate">{project.title}</h3>
                    <p className="text-xs text-muted-foreground truncate">{project.id.substring(0, 8)}</p>
                  </div>
                </div>
                <div className="col-span-2">
                  <span className={cn('text-xs px-2.5 py-1 rounded-full border', getStatusBg(project.status))}>
                    {project.status}
                  </span>
                </div>
                <div className="col-span-2 capitalize text-sm text-muted-foreground">
                  {project.input_type}
                </div>
                <div className="col-span-3 flex items-center gap-1.5 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  {formatRelativeTime(project.created_at)}
                </div>
                <div className="col-span-1 flex justify-end">
                  <ChevronRight className="w-5 h-5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
