'use client'

import { useCallback } from 'react'
import { create } from 'zustand'
import { useSession } from 'next-auth/react'

export type QueueItemStatus =
  | 'pending'
  | 'uploading'
  | 'uploaded'
  | 'error'
  | 'cancelled'

export interface QueueItem {
  id: string          // client-side UUID
  file: File
  status: QueueItemStatus
  progress: number    // 0-100
  jobId?: string      // server job ID once created
  error?: string
  abortController?: AbortController
}

interface UploadQueueState {
  items: QueueItem[]
  addFiles: (files: File[]) => void
  removeItem: (id: string) => void
  cancelItem: (id: string) => void
  clearCompleted: () => void
  _updateItem: (id: string, patch: Partial<QueueItem>) => void
}

// Zustand store — persists across component remounts during a session
export const useUploadQueueStore = create<UploadQueueState>((set, get) => ({
  items: [],

  addFiles: (files) => {
    const newItems: QueueItem[] = files.map((file) => ({
      id: crypto.randomUUID(),
      file,
      status: 'pending',
      progress: 0,
    }))
    set((state) => ({ items: [...state.items, ...newItems] }))
  },

  removeItem: (id) => {
    const item = get().items.find((i) => i.id === id)
    item?.abortController?.abort()
    set((state) => ({ items: state.items.filter((i) => i.id !== id) }))
  },

  cancelItem: (id) => {
    const item = get().items.find((i) => i.id === id)
    item?.abortController?.abort()
    set((state) => ({
      items: state.items.map((i) =>
        i.id === id ? { ...i, status: 'cancelled' as const, progress: 0 } : i,
      ),
    }))
  },

  clearCompleted: () => {
    set((state) => ({
      items: state.items.filter(
        (i) => i.status !== 'uploaded' && i.status !== 'cancelled',
      ),
    }))
  },

  _updateItem: (id, patch) => {
    set((state) => ({
      items: state.items.map((i) => (i.id === id ? { ...i, ...patch } : i)),
    }))
  },
}))

const MAX_CONCURRENT = 3
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const ALLOWED_EXTENSIONS = new Set(['mp3', 'wav', 'aac', 'm4a', 'flac', 'ogg'])
const MAX_SIZE_BYTES = 500 * 1024 * 1024 // 500 MB

/**
 * useUploadQueue — provides upload actions bound to the current session token.
 * Call `upload(files)` to validate, enqueue, and start uploading files.
 */
export function useUploadQueue() {
  const { data: session } = useSession()
  const token = session?.accessToken
  const { items, addFiles, removeItem, cancelItem, clearCompleted, _updateItem } =
    useUploadQueueStore()

  const upload = useCallback(
    async (files: File[]) => {
      if (!token) return

      // Validate each file before adding to queue
      const valid: File[] = []
      const errors: string[] = []

      for (const file of files) {
        const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
        if (!ALLOWED_EXTENSIONS.has(ext)) {
          errors.push(`${file.name}: unsupported format`)
          continue
        }
        if (file.size > MAX_SIZE_BYTES) {
          errors.push(`${file.name}: exceeds 500 MB limit`)
          continue
        }
        if (file.size === 0) {
          errors.push(`${file.name}: file is empty`)
          continue
        }
        valid.push(file)
      }

      if (valid.length === 0) return { errors }

      addFiles(valid)

      // Limit concurrent uploads
      const pending = useUploadQueueStore
        .getState()
        .items.filter((i) => i.status === 'pending')
        .slice(0, MAX_CONCURRENT)

      await Promise.allSettled(pending.map((item) => _uploadOne(item.id, token, _updateItem)))

      return { errors }
    },
    [token, addFiles, _updateItem],
  )

  const retry = useCallback(
    async (itemId: string) => {
      if (!token) return
      _updateItem(itemId, { status: 'pending', progress: 0, error: undefined })
      await _uploadOne(itemId, token, _updateItem)
    },
    [token, _updateItem],
  )

  return { items, upload, retry, removeItem, cancelItem, clearCompleted }
}

async function _uploadOne(
  itemId: string,
  token: string,
  update: UploadQueueState['_updateItem'],
): Promise<void> {
  const item = useUploadQueueStore.getState().items.find((i) => i.id === itemId)
  if (!item || item.status === 'cancelled') return

  const abort = new AbortController()
  update(itemId, { status: 'uploading', abortController: abort })

  return new Promise<void>((resolve) => {
    const formData = new FormData()
    formData.append('file', item.file)

    const xhr = new XMLHttpRequest()

    abort.signal.addEventListener('abort', () => {
      xhr.abort()
      resolve()
    })

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        update(itemId, { progress: Math.round((e.loaded / e.total) * 100) })
      }
    }

    xhr.onload = () => {
      if (xhr.status === 201) {
        const job = JSON.parse(xhr.response)
        update(itemId, { status: 'uploaded', progress: 100, jobId: job.id })
      } else {
        const detail =
          JSON.parse(xhr.response || '{}').detail ?? `Upload failed (${xhr.status})`
        update(itemId, { status: 'error', error: detail })
      }
      resolve()
    }

    xhr.onerror = () => {
      update(itemId, { status: 'error', error: 'Network error. Check your connection.' })
      resolve()
    }

    xhr.onabort = () => {
      update(itemId, { status: 'cancelled', progress: 0 })
      resolve()
    }

    xhr.open('POST', `${API_URL}/api/v1/jobs/upload`)
    xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.send(formData)
  })
}
