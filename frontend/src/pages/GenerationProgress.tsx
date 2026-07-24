import { useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { CheckCircle2, XCircle, Loader2, Terminal, ArrowRight } from 'lucide-react'
import { useJobProgress } from '@/hooks/useJobProgress'
import { useQueryClient } from '@tanstack/react-query'
import { useJobStatus } from '@/hooks/useProjects'
import { PIPELINE_STAGES } from '@/types'
import { cn, formatRelativeTime } from '@/lib/utils'

function StageRow({ stage, status }: { stage: typeof PIPELINE_STAGES[number]; status: 'pending' | 'active' | 'done' | 'error' }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'flex items-center gap-3 p-3 rounded-lg transition-all',
        status === 'active' && 'bg-primary/10 border border-primary/30',
        status === 'done' && 'opacity-70',
        status === 'error' && 'bg-red-500/10 border border-red-500/30',
      )}
    >
      <div className="w-7 h-7 rounded-full flex items-center justify-center text-sm shrink-0">
        {status === 'done' && <CheckCircle2 className="w-5 h-5 text-green-400" />}
        {status === 'active' && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
        {status === 'error' && <XCircle className="w-5 h-5 text-red-400" />}
        {status === 'pending' && <div className="w-3 h-3 rounded-full bg-white/20" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm">{stage.icon}</span>
          <span className={cn('text-sm font-medium', status === 'pending' && 'text-muted-foreground')}>
            {stage.label}
          </span>
        </div>
      </div>
      {status === 'active' && (
        <div className="flex gap-0.5">
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
              className="w-1 h-1 rounded-full bg-primary"
            />
          ))}
        </div>
      )}
    </motion.div>
  )
}

export function GenerationProgress() {
  const navigate = useNavigate()
  const { projectId } = useParams<{ projectId: string }>()
  const [searchParams] = useSearchParams()
  const jobId = searchParams.get('job')

  const { currentStage, progressPercent, isComplete, hasError, errorMessage, events } = useJobProgress(jobId)
  const { data: job, refetch } = useJobStatus(jobId)
  const queryClient = useQueryClient()

  useEffect(() => {
    if (isComplete) {
      refetch()
      queryClient.invalidateQueries({ queryKey: ['videos', projectId] })
      setTimeout(() => navigate(`/projects/${projectId}`), 2000)
    }
  }, [isComplete, navigate, projectId, refetch, queryClient])

  const getStageStatus = (stageId: string) => {
    if (!job) return 'pending'
    if (job.stages_completed?.includes(stageId)) return 'done'
    if (currentStage === stageId) return 'active'
    if (hasError && job.error_stage === stageId) return 'error'
    return 'pending'
  }

  const logs = events.filter(e => e.event_type === 'log').slice(-20).reverse()

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Generating Your Video</h1>
        <p className="text-muted-foreground mt-1">AI is working through the pipeline — this may take a few minutes</p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Pipeline stages */}
        <div className="col-span-3 space-y-4">
          {/* Progress bar */}
          <div className="glass rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm font-bold text-primary">{progressPercent}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-purple-hot rounded-full"
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* Stages */}
          <div className="glass rounded-xl p-4 space-y-1">
            <h3 className="text-sm font-semibold mb-3 px-2">Pipeline Stages</h3>
            {PIPELINE_STAGES.map((stage) => (
              <StageRow key={stage.id} stage={stage} status={getStageStatus(stage.id)} />
            ))}
          </div>

          {/* Completion / Error */}
          {isComplete && (
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass rounded-xl p-6 text-center border border-green-500/30 bg-green-500/5"
            >
              <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-3" />
              <h3 className="font-bold text-lg">Video Generated Successfully!</h3>
              <p className="text-muted-foreground text-sm mt-1">Redirecting to project details...</p>
            </motion.div>
          )}

          {hasError && (
            <div className="glass rounded-xl p-5 border border-red-500/30 bg-red-500/5">
              <div className="flex items-center gap-2 mb-2">
                <XCircle className="w-5 h-5 text-red-400" />
                <h3 className="font-semibold">Generation Failed</h3>
              </div>
              <p className="text-sm text-muted-foreground">{errorMessage}</p>
              <button
                onClick={() => navigate(`/projects/${projectId}`)}
                className="mt-4 flex items-center gap-2 text-sm text-primary hover:text-primary/80"
              >
                Back to project <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        {/* Logs panel */}
        <div className="col-span-2">
          <div className="glass rounded-xl p-4 h-full">
            <div className="flex items-center gap-2 mb-3">
              <Terminal className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-semibold">Live Logs</h3>
            </div>
            <div className="space-y-1.5 overflow-y-auto max-h-96">
              {logs.length === 0 ? (
                <p className="text-xs text-muted-foreground">Waiting for pipeline...</p>
              ) : (
                logs.map((event, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs font-mono"
                  >
                    <span className="text-muted-foreground">[{event.stage}]</span>{' '}
                    <span className={event.metadata?.status === 'error' ? 'text-red-400' : 'text-green-400/90'}>
                      {event.message}
                    </span>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
