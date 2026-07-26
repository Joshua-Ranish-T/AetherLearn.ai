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
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-slate-200 shadow-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 text-sm text-slate-800 placeholder:text-slate-400 transition-all"
          />
        </div>
        <div className="flex items-center gap-1.5 glass rounded-xl p-1.5 border border-slate-200 shadow-sm bg-white/80">
          {['all', 'completed', 'running', 'failed'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f as typeof filter)}
              className={cn(
                'px-4 py-1.5 rounded-lg text-sm font-semibold capitalize transition-all',
                filter === f ? 'bg-primary text-white shadow-md shadow-primary/25' : 'hover:bg-slate-100 text-slate-600'
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* List */}
      <div className="glass rounded-2xl overflow-hidden border border-slate-200/80 shadow-lg shadow-slate-200/50 bg-white/90">
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-slate-200/80 bg-slate-100/90 text-sm font-semibold text-slate-700">
          <div className="col-span-4">Project Name</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2">Input Type</div>
          <div className="col-span-3">Created</div>
          <div className="col-span-1"></div>
        </div>

        {isLoading ? (
          <div className="divide-y divide-slate-100">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="p-4 h-16 shimmer" />
            ))}
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="p-12 text-center text-slate-500 font-medium">
            No projects found matching your criteria.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredProjects.map((project, i) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.05 }}
                className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-green-50/50 transition-all cursor-pointer group hover:pl-5"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <div className="col-span-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-green-50 border border-green-200/60 flex items-center justify-center shrink-0 shadow-sm group-hover:scale-105 transition-transform">
                    <VideoIcon className="w-5 h-5 text-[#1BC237]" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-sm text-slate-800 truncate group-hover:text-[#1BC237] transition-colors">{project.title}</h3>
                    <p className="text-xs text-slate-400 truncate font-mono">{project.id.substring(0, 8)}</p>
                  </div>
                </div>
                <div className="col-span-2">
                  <span className={cn('text-xs px-2.5 py-1 rounded-full border', getStatusBg(project.status))}>
                    {project.status}
                  </span>
                </div>
                <div className="col-span-2 capitalize text-sm font-medium text-slate-600">
                  {project.input_type}
                </div>
                <div className="col-span-3 flex items-center gap-1.5 text-sm font-medium text-slate-500">
                  <Clock className="w-4 h-4 text-slate-400" />
                  {formatRelativeTime(project.created_at)}
                </div>
                <div className="col-span-1 flex justify-end">
                  <ChevronRight className="w-5 h-5 text-slate-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
