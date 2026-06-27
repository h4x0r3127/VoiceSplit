export interface ApiError {
  detail: string
  status: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  perPage: number
}

export type ExportFormat = 'mp3' | 'wav' | 'flac' | 'txt' | 'json' | 'csv'

export interface Export {
  id: string
  jobId: string
  speakerIds: string[]
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED'
  outputFormat: ExportFormat
  downloadUrl?: string
  fileSizeBytes?: number
  createdAt: string
  updatedAt: string
}

export interface TokenResponse {
  accessToken: string
  tokenType: string
  expiresIn: number
  user: {
    id: string
    email: string
    name: string
    avatarUrl?: string
    credits: number
    storageUsedBytes: number
    createdAt: string
  }
}

export interface PresignedUploadResponse {
  jobId: string
  uploadUrl: string
  fields: Record<string, string>
}
