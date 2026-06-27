'use client'

import { useState, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { uploadAudio } from '@/services/jobs.service'
import type { Job } from '@/types/job'

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error'

export function useUpload() {
  const { data: session } = useSession()
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<UploadStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [job, setJob] = useState<Job | null>(null)

  const upload = useCallback(
    async (file: File): Promise<Job | null> => {
      if (!session?.accessToken) {
        setError('Not authenticated')
        return null
      }

      setStatus('uploading')
      setProgress(0)
      setError(null)

      try {
        const result = await uploadAudio(session.accessToken, file, setProgress)
        setJob(result)
        setStatus('success')
        return result
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed'
        setError(message)
        setStatus('error')
        return null
      }
    },
    [session?.accessToken],
  )

  const reset = useCallback(() => {
    setProgress(0)
    setStatus('idle')
    setError(null)
    setJob(null)
  }, [])

  return { upload, progress, status, error, job, reset }
}
