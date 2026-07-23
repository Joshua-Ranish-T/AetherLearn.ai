import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, Download, FileText, Code2, Volume2 } from 'lucide-react'
import { videoService } from '@/services/generationService'
import { formatDuration } from '@/lib/utils'

export function VideoPreview() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()

  const { data: video, isLoading } = useQuery({
    queryKey: ['video', videoId],
    queryFn: () => videoService.getById(videoId!),
    enabled: !!videoId,
  })

  if (isLoading) return <div className="glass rounded-xl h-96 shimmer animate-fade-in" />
  if (!video) return <div className="text-center py-20 text-muted-foreground">Video not found</div>

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="glass p-2 rounded-lg hover:bg-white/10">
          <ArrowLeft className="w-4 h-4" />
        </button>
        <div>
          <h1 className="text-xl font-bold">{video.title}</h1>
          <p className="text-sm text-muted-foreground">{formatDuration(video.duration_seconds)} • {video.resolution}</p>
        </div>
      </div>

      {/* Video player */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl overflow-hidden border border-white/15 shadow-2xl shadow-black/50"
      >
        {video.file_url ? (
          <video
            controls
            className="w-full rounded-2xl"
            style={{ maxHeight: '60vh' }}
            src={video.file_url}
          >
            Your browser does not support video playback.
          </video>
        ) : (
          <div className="aspect-video flex items-center justify-center bg-black/40 rounded-2xl">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-3">
                <Volume2 className="w-8 h-8 text-muted-foreground" />
              </div>
              <p className="text-muted-foreground text-sm">Video URL not available</p>
            </div>
          </div>
        )}
      </motion.div>

      {/* Downloads & metadata */}
      <div className="grid grid-cols-3 gap-4">
        {video.file_url && (
          <a href={video.file_url} target="_blank" rel="noreferrer" className="glass-hover rounded-xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 bg-primary/20 rounded-lg flex items-center justify-center">
              <Download className="w-4 h-4 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium">Download Video</p>
              <p className="text-xs text-muted-foreground">MP4 file</p>
            </div>
          </a>
        )}
        {video.transcript_url && (
          <a href={video.transcript_url} target="_blank" rel="noreferrer" className="glass-hover rounded-xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 bg-green-500/20 rounded-lg flex items-center justify-center">
              <FileText className="w-4 h-4 text-green-400" />
            </div>
            <div>
              <p className="text-sm font-medium">Transcript</p>
              <p className="text-xs text-muted-foreground">TXT file</p>
            </div>
          </a>
        )}
        {video.manim_script_url && (
          <a href={video.manim_script_url} target="_blank" rel="noreferrer" className="glass-hover rounded-xl p-4 flex items-center gap-3">
            <div className="w-9 h-9 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <Code2 className="w-4 h-4 text-yellow-400" />
            </div>
            <div>
              <p className="text-sm font-medium">Manim Script</p>
              <p className="text-xs text-muted-foreground">Python source</p>
            </div>
          </a>
        )}
      </div>
    </div>
  )
}
