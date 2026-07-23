import { useEffect, useRef, useState, useCallback } from 'react';
import type { ProgressEvent } from '@/types';
import { generationService } from '@/services/generationService';

interface UseJobProgressOptions {
  onStageStart?: (event: ProgressEvent) => void;
  onLog?: (event: ProgressEvent) => void;
  onComplete?: (event: ProgressEvent) => void;
  onError?: (event: ProgressEvent) => void;
}

interface JobProgressState {
  events: ProgressEvent[];
  currentStage: string;
  progressPercent: number;
  isComplete: boolean;
  hasError: boolean;
  errorMessage: string;
}

/**
 * Hook that subscribes to SSE progress stream for a job.
 * Automatically reconnects on connection loss.
 */
export function useJobProgress(
  jobId: string | null,
  options: UseJobProgressOptions = {}
) {
  const [state, setState] = useState<JobProgressState>({
    events: [],
    currentStage: '',
    progressPercent: 0,
    isComplete: false,
    hasError: false,
    errorMessage: '',
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const { onStageStart, onLog, onComplete, onError } = options;

  const connect = useCallback(() => {
    if (!jobId) return;

    const url = generationService.getStreamUrl(jobId);
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data: ProgressEvent = JSON.parse(event.data);

        if (data.event_type === 'close') {
          es.close();
          return;
        }

        setState((prev) => ({
          ...prev,
          events: [...prev.events, data],
          currentStage: data.stage || prev.currentStage,
          progressPercent: data.progress_percent,
          isComplete: data.event_type === 'done',
          hasError: data.event_type === 'error',
          errorMessage:
            data.event_type === 'error'
              ? (data.metadata?.error as string) || data.message
              : prev.errorMessage,
        }));

        // Callbacks
        if (data.event_type === 'stage_start') onStageStart?.(data);
        if (data.event_type === 'log') onLog?.(data);
        if (data.event_type === 'done') {
          onComplete?.(data);
          es.close();
        }
        if (data.event_type === 'error') {
          onError?.(data);
          es.close();
        }
      } catch {
        // Ignore parse errors
      }
    };

    es.onerror = () => {
      es.close();
      // Reconnect after 3s if not complete
      setState((prev) => {
        if (!prev.isComplete && !prev.hasError) {
          setTimeout(connect, 3000);
        }
        return prev;
      });
    };
  }, [jobId, onStageStart, onLog, onComplete, onError]);

  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
    };
  }, [connect]);

  const reset = useCallback(() => {
    eventSourceRef.current?.close();
    setState({
      events: [],
      currentStage: '',
      progressPercent: 0,
      isComplete: false,
      hasError: false,
      errorMessage: '',
    });
  }, []);

  return { ...state, reset };
}
