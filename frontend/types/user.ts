export interface User {
  id: string
  email: string
  name: string
  avatarUrl?: string
  credits: number
  storageUsedBytes: number
  createdAt: string
}

export interface UserAnalytics {
  totalJobs: number
  completedJobs: number
  totalMinutesProcessed: number
  totalSpeakersFound: number
  storageUsedBytes: number
}

export interface UserSettings {
  notifications: {
    jobComplete: boolean
    weeklyReport: boolean
    marketing: boolean
  }
  defaultExportFormat: 'mp3' | 'wav' | 'flac'
  defaultExportQuality: 'low' | 'medium' | 'high'
  apiKey?: string
}
