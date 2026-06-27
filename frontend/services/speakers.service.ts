import { api } from './api'
import type { Speaker } from '@/types/speaker'

const BASE = '/api/v1/speakers'

export async function getSpeaker(token: string, id: string): Promise<Speaker> {
  return api.get<Speaker>(`${BASE}/${id}`, { token })
}

export async function getSpeakerPreviewUrl(token: string, id: string): Promise<string> {
  const data = await api.get<{ url: string }>(`${BASE}/${id}/preview`, { token })
  return data.url
}

export async function updateSpeakerLabel(token: string, id: string, label: string): Promise<Speaker> {
  return api.patch<Speaker>(`${BASE}/${id}`, { label }, { token })
}
