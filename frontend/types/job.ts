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
  { key: 'PREPROCESSING', label: 'Noise Reduction', description: 'Cleaning audio and removing background noise' },
  { key: 'VAD', label: 'Voice Detection', description: 'Detecting regions of human speech' },
  { key: 'DIARIZING', label: 'Speaker Diarization', description: 'Identifying who speaks when' },
  { key: 'EMBEDDING', label: 'Voice Embeddings', description: 'Creating unique voice fingerprints' },
  { key: 'CLUSTERING', label: 'Clustering', description: 'Grouping speech segments by speaker' },
  { key: 'SEPARATING', label: 'Speech Separation', description: 'Isolating each speaker\'s audio' },
  { key: 'TRANSCRIBING', label: 'Transcription', description: 'Converting speech to text' },
  { key: 'ANALYZING', label: 'Analysis', description: 'Computing speaker statistics' },
  { key: 'RECONSTRUCTING', label: 'Reconstruction', description: 'Generating final audio files' },
]

export interface Job {
  id: string
  userId: string
  originalFilename: string
  status: JobStatus
  pipelineStage?: string
  progress: number
  durationSeconds?: number
  fileSizeBytes: number
  errorMessage?: string
  speakers: Speaker[]
  createdAt: string
  updatedAt: string
}

export interface JobProgress {
  jobId: string
  stage: string
  progress: number
  message: string
}

export interface TranscriptSegment {
  id: string
  speakerId: string
  speakerLabel: string
  speakerColor: string
  startTime: number
  endTime: number
  text: string
  confidence: number
}
