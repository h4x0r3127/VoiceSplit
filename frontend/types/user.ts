export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  credits: number
  storage_used_bytes: number
  is_verified: boolean
  created_at: string
}

export interface UserAnalytics {
  total_jobs: number
  completed_jobs: number
  total_minutes_processed: number
  total_speakers_found: number
  storage_used_bytes: number
}

export interface UserSettings {
  notifications: {
    job_complete: boolean
    weekly_report: boolean
    marketing: boolean
  }
  default_export_format: 'mp3' | 'wav' | 'flac'
  default_export_quality: 'low' | 'medium' | 'high'
  api_key?: string
}
