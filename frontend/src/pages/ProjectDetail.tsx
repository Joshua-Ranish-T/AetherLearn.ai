import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Play, Download, Code2, FileText, Layers, Clock, RefreshCw, ArrowLeft, Sparkles } from 'lucide-react'
import { projectsService } from '@/services/projectsService'
import { videoService } from '@/services/generationService'
import { useStartGeneration } from '@/hooks/useProjects'
import { formatDuration, formatRelativeTime, getStatusBg, cn } from '@/lib/utils'

export function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const startGeneration = useStartGeneration()

  const { data: project, isLoading: loadingProject } = useQuery({
    queryKey: ['projects', projectId],
    queryFn: () => projectsService.getById(projectId!),
    enabled: !!projectId,
  })

  const { data: videos, isLoading: loadingVideos } = useQuery({
    queryKey: ['videos', projectId],
    queryFn: () => videoService.getByProject(projectId!),
    enabled: !!projectId,
  })

  const latestVideo = videos?.[0]

  const handleRegenerate = async () => {
    if (!projectId) return
    const job = await startGeneration.mutateAsync({
      project_id: projectId,
      force_regenerate: true,
    })
    navigate(`/projects/${projectId}/generate?job=${job.id}`)
  }

  if (loadingProject) {
    return <div className="animate-fade-in"><div className="glass rounded-xl h-64 shimmer" /></div>
  }

  if (!project) {
    return <div className="text-center py-20 text-muted-foreground">Project not found</div>
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="glass p-2 rounded-lg hover:bg-white/10">
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold">{project.title}</h1>
            <div className="flex items-center gap-3 mt-1">
              <span className={cn('text-xs px-2 py-0.5 rounded-full border', getStatusBg(project.status))}>
                {project.status}
              </span>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="w-3 h-3" />{formatRelativeTime(project.created_at)}
              </span>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {latestVideo && (
            <button
              onClick={() => navigate(`/videos/${latestVideo.id}`)}
              className="btn-glow bg-primary text-white px-4 py-2 rounded-xl text-sm font-medium flex items-center gap-2"
            >
              <Play className="w-4 h-4" /> Watch Video
            </button>
          )}
          <button
            onClick={handleRegenerate}
            disabled={startGeneration.isPending}
            className="glass px-4 py-2 rounded-xl text-sm flex items-center gap-2 hover:bg-white/10"
          >
            <RefreshCw className={cn('w-4 h-4', startGeneration.isPending && 'animate-spin')} />
            Regenerate
          </button>
        </div>
      </div>

      {/* Video card */}
      {latestVideo && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-xl overflow-hidden border border-primary/20"
        >
          <div className="p-5 flex items-center justify-between border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center">
                <Play className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">{latestVideo.title}</h3>
                <p className="text-xs text-muted-foreground">{formatDuration(latestVideo.duration_seconds)} • {latestVideo.resolution}</p>
              </div>
            </div>
            <div className="flex gap-2">
              {latestVideo.file_url && (
                <a href={latestVideo.file_url} target="_blank" rel="noreferrer"
                   className="glass px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 hover:bg-white/10">
                  <Download className="w-3 h-3" /> Download MP4
                </a>
              )}
              {latestVideo.transcript_url && (
                <a href={latestVideo.transcript_url} target="_blank" rel="noreferrer"
                   className="glass px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 hover:bg-white/10">
                  <FileText className="w-3 h-3" /> Transcript
                </a>
              )}
              {latestVideo.manim_script_url && (
                <a href={latestVideo.manim_script_url} target="_blank" rel="noreferrer"
                   className="glass px-3 py-1.5 rounded-lg text-xs flex items-center gap-1.5 hover:bg-white/10">
                  <Code2 className="w-3 h-3" /> Script
                </a>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Project info */}
      <div className="grid grid-cols-2 gap-5">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary" /> Input Content
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Type</span>
              <span className="capitalize">{project.input_type}</span>
            </div>
            {project.input_text && (
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-1">Content Preview</p>
                <p className="text-xs bg-black/30 rounded-lg p-3 line-clamp-6 font-mono">
                  {project.input_text}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary" /> Video Details
          </h3>
          {latestVideo ? (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Duration</span>
                <span>{formatDuration(latestVideo.duration_seconds)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Resolution</span>
                <span>{latestVideo.resolution}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subject</span>
                <span className="capitalize">{(latestVideo.metadata?.subject as string) || 'General'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Difficulty</span>
                <span className="capitalize">{(latestVideo.metadata?.difficulty as string) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Scenes</span>
                <span>{(latestVideo.metadata?.scene_count as number) || 'N/A'}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">No video generated yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
