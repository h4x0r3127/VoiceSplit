import { api } from './api'
import type { Export, ExportFormat } from '@/types/api'

const BASE = '/api/v1/exports'

export async function createExport(
  token: string,
  jobId: string,
  speakerIds: string[],
  format: ExportFormat,
): Promise<Export> {
  return api.post<Export>(BASE, { jobId, speakerIds, format }, { token })
}

export async function getExport(token: string, id: string): Promise<Export> {
  return api.get<Export>(`${BASE}/${id}`, { token })
}
