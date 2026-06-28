export interface SpeakerSegment {
  start: number
  end: number
  confidence: number
}

export interface Speaker {
  id: string
  job_id: string
  label: string
  color: string
  gender?: 'male' | 'female' | 'unknown'
  age_range?: string
  language?: string
  speaking_duration: number
  confidence: number
  emotion?: string
  accent?: string
  preview_s3_key?: string
  segments: SpeakerSegment[]
}

export const SPEAKER_COLORS = [
  '#06D6CF', // brand cyan
  '#3B82F6', // brand blue
  '#7C3AED', // brand purple
  '#F59E0B', // amber
  '#EC4899', // pink
  '#10B981', // emerald
  '#F97316', // orange
  '#6366F1', // indigo
] as const

export function getSpeakerColor(index: number): string {
  return SPEAKER_COLORS[index % SPEAKER_COLORS.length]
}
