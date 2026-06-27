import { api } from './api'
import type { Job, TranscriptSegment } from '@/types/job'
import type { PaginatedResponse } from '@/types/api'

const BASE = '/api/v1/jobs'

export async function getJobs(
  token: string,
  page = 1,
  status?: string,
): Promise<PaginatedResponse<Job>> {
  return api.get<PaginatedResponse<Job>>(BASE, {
    token,
    params: { page, per_page: 20, status },
  })
}

export async function getJob(token: string, id: string): Promise<Job> {
  return api.get<Job>(`${BASE}/${id}`, { token })
}

export async function deleteJob(token: string, id: string): Promise<void> {
  return api.delete<void>(`${BASE}/${id}`, { token })
}

export async function processJob(
  token: string,
  id: string,
  selectedSpeakerIds: string[],
): Promise<void> {
  return api.post<void>(`${BASE}/${id}/process`, { speakerIds: selectedSpeakerIds }, { token })
}

export async function getTranscript(token: string, id: string): Promise<TranscriptSegment[]> {
  return api.get<TranscriptSegment[]>(`${BASE}/${id}/transcript`, { token })
}

export async function uploadAudio(
  token: string,
  file: File,
  onProgress: (percent: number) => void,
): Promise<Job> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const formData = new FormData()
  formData.append('file', file)

  return new Promise<Job>((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.response) as Job)
      } else {
        try {
          const err = JSON.parse(xhr.response)
          reject(new Error(err.detail || 'Upload failed'))
        } catch {
          reject(new Error('Upload failed'))
        }
      }
    }

    xhr.onerror = () => reject(new Error('Network error during upload'))

    xhr.open('POST', `${API_URL}${BASE}/upload`)
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(formData)
  })
}
