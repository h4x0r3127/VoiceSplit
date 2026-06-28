import type { Speaker } from './speaker'

export type JobStatus =
  | 'UPLOADED'
  | 'PREPROCESSING'
  | 'VAD'
  | 'DIARIZING'
  | 'EMBEDDING'
  | 'CLUSTERING'
  | 'SEPARATING'
  | 'TRANSCRIBING'
  | 'ANALYZING'
  | 'RECONSTRUCTING'
  | 'COMPLETED'
  | 'FAILED'

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  UPLOADED: 'Uploaded',
  PREPROCESSING: 'Preprocessing',
  VAD: 'Voice Detection',
  DIARIZING: 'Speaker Diarization',
  EMBEDDING: 'Voice Embeddings',
  CLUSTERING: 'Clustering',
  SEPARATING: 'Separating',
  TRANSCRIBING: 'Transcribing',
  ANALYZING: 'Analyzing',
  RECONSTRUCTING: 'Reconstructing',
  COMPLETED: 'Completed',
  FAILED: 'Failed',
}

export const PIPELINE_STAGES: Array<{ key: string; label: string; description: string }> = [
  { key: 'PREPROCESSING', label: 'Noise Reduction',     description: 'Cleaning audio and removing background noise' },
  { key: 'VAD',           label: 'Voice Detection',     description: 'Detecting regions of human speech' },
  { key: 'DIARIZING',     label: 'Speaker Diarization', description: 'Identifying who speaks when' },
  { key: 'EMBEDDING',     label: 'Voice Embeddings',    description: 'Creating unique voice fingerprints' },
  { key: 'CLUSTERING',    label: 'Clustering',          description: 'Grouping speech segments by speaker' },
  { key: 'SEPARATING',    label: 'Speech Separation',   description: 'Isolating each speaker\'s audio' },
  { key: 'TRANSCRIBING',  label: 'Transcription',       description: 'Converting speech to text' },
  { key: 'ANALYZING',     label: 'Analysis',            description: 'Computing speaker statistics' },
  { key: 'RECONSTRUCTING',label: 'Reconstruction',      description: 'Generating final audio files' },
]

export interface Job {
  id: string
  user_id: string
  original_filename: string
  original_s3_key: string
  processed_s3_key?: string
  status: JobStatus
  pipeline_stage?: string
  progress: number
  duration_seconds?: number
  file_size_bytes: number
  error_message?: string
  audio_metadata?: Record<string, unknown>
  speakers: Speaker[]
  created_at: string
  updated_at: string
}

export interface JobProgress {
  job_id: string
  stage: string
  progress: number
  message: string
}

export interface TranscriptSegment {
  id: string
  speaker_id: string
  speaker_label: string
  speaker_color: string
  start_time: number
  end_time: number
  text: string
  confidence: number
}
