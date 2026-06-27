'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import type { JobProgress } from '@/types/job'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error'

export function useJobProgress(jobId: string | null) {
  const { data: session } = useSession()
  const [progress, setProgress] = useState<JobProgress | null>(null)
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const retryCountRef = useRef(0)
  const MAX_RETRIES = 5

  const connect = useCallback(() => {
    if (!jobId || !session?.accessToken) return

    const ws = new WebSocket(
      `${WS_URL}/api/v1/ws/jobs/${jobId}?token=${session.accessToken}`,
    )

    setConnectionState('connecting')

    ws.onopen = () => {
      setConnectionState('connected')
      retryCountRef.current = 0
    }

    ws.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data as string) as JobProgress
        setProgress(data)
      } catch {
        // malformed message — ignore
      }
    }

    ws.onerror = () => {
      setConnectionState('error')
    }

    ws.onclose = () => {
      setConnectionState('disconnected')
      wsRef.current = null

      if (retryCountRef.current < MAX_RETRIES) {
        const delay = Math.min(1000 * 2 ** retryCountRef.current, 30000)
        retryCountRef.current += 1
        retryTimeoutRef.current = setTimeout(connect, delay)
      }
    }

    wsRef.current = ws
  }, [jobId, session?.accessToken])

  useEffect(() => {
    if (!jobId) return
    connect()

    return () => {
      if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null
        wsRef.current.close()
      }
    }
  }, [jobId, connect])

  return { progress, connectionState }
}
