// Project and Job types matching backend Pydantic schemas

export type InputType = 'text' | 'topic' | 'pdf' | 'image' | 'screenshot' | 'handwritten';
export type GenerationStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Project {
  id: string;
  title: string;
  description: string;
  input_type: InputType;
  input_text: string;
  input_file_url: string;
  status: GenerationStatus;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
}

export interface ProjectCreate {
  title: string;
  description?: string;
  input_type: InputType;
  input_text?: string;
  metadata?: Record<string, unknown>;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  limit: number;
  offset: number;
}

export interface Job {
  id: string;
  project_id: string;
  status: GenerationStatus;
  current_stage: string;
  stages_completed: string[];
  error_message: string;
  error_stage: string;
  retry_count: number;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number;
  logs: LogEntry[];
}

export interface LogEntry {
  stage: string;
  status: string;
  message: string;
  timestamp: string;
  [key: string]: unknown;
}

export interface Video {
  id: string;
  project_id: string;
  job_id: string;
  title: string;
  duration_seconds: number;
  resolution: string;
  file_url: string;
  audio_url: string;
  transcript_url: string;
  manim_script_url: string;
  storyboard_url: string;
  thumbnail_url: string;
  file_size_bytes: number;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface GenerationRequest {
  project_id: string;
  force_regenerate?: boolean;
  quality?: 'low_quality' | 'medium_quality' | 'high_quality';
  tts_engine?: 'edge-tts' | 'gtts';
  tts_voice?: string;
}

export interface ProgressEvent {
  event_type: 'stage_start' | 'stage_complete' | 'log' | 'error' | 'done' | 'close';
  job_id: string;
  stage: string;
  message: string;
  progress_percent: number;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface StoryboardScene {
  scene_number: number;
  scene_title: string;
  learning_objective: string;
  animation_description: string;
  voice_segment: string;
  estimated_duration_seconds: number;
  background_color: string;
  transition: string;
  mathematical_expressions: string[];
  code_snippet: string;
  objects: SceneObject[];
  animations: SceneAnimation[];
}

export interface SceneObject {
  object_type: string;
  content: string;
  position: string;
  color: string;
  scale: number;
}

export interface SceneAnimation {
  animation_type: string;
  target_object: string;
  duration: number;
  parameters: Record<string, string>;
}

export const PIPELINE_STAGES = [
  { id: 'supervisor', label: 'Analyzing Input', icon: '🎯' },
  { id: 'ocr_agent', label: 'Extracting Content', icon: '📖' },
  { id: 'content_generation_agent', label: 'Generating Lesson', icon: '🧠' },
  { id: 'manim_script_agent', label: 'Writing Animation Code', icon: '✍️' },
  { id: 'manim_execution_service', label: 'Rendering Animation', icon: '🎬' },
  { id: 'repair_agent', label: 'Fixing Errors', icon: '🔧' },
  { id: 'narration_agent', label: 'Generating Narration', icon: '🎙️' },
  { id: 'synchronization_service', label: 'Syncing Audio & Video', icon: '🎵' },
  { id: 'finalize', label: 'Finalizing Video', icon: '✅' },
];
