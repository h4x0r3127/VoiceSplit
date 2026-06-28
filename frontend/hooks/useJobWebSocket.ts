'use client'

import { useEffect, useRef, useState, useCallback } from 'react'

export interface JobProgressEvent {
  job_id: string
  status: string
  stage: string
  progress: number
  message: string
  error?: string | null
  type?: 'ping'
}

interface UseJobWebSocketOptions {
  jobId: string
  token: string | undefined
  onComplete?: (event: JobProgressEvent) => void
  onFailed?: (event: JobProgressEvent) => void
  enabled?: boolean
}

interface UseJobWebSocketReturn {
  latest: JobProgressEvent | null
  isConnected: boolean
  isTerminal: boolean
  error: string | null
}

const TERMINAL_STATUSES = new Set(['COMPLETED', 'FAILED'])
const MAX_RECONNECT_ATTEMPTS = 5
const RECONNECT_DELAY_MS = 2000

/**
 * Connects to the VoiceSplit WebSocket job progress endpoint.
 * Automatically reconnects on drop with exponential backoff.
 * Stops connecting once the job reaches a terminal status.
 */
export function useJobWebSocket({
  jobId,
  token,
  onComplete,
  onFailed,
  enabled = true,
}: UseJobWebSocketOptions): UseJobWebSocketReturn {
  const [latest, setLatest] = useState<JobProgressEvent | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isTerminal, setIsTerminal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectAttempts = useRef(0)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isTerminalRef = useRef(false)

  const connect = useCallback(() => {
    if (!token || !enabled || isTerminalRef.current) return

    const wsBase = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000'
    const url = `${wsBase}/api/v1/ws/jobs/${jobId}?token=${encodeURIComponent(token)}`

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      setError(null)
      reconnectAttempts.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const data: JobProgressEvent = JSON.parse(event.data)

        // Ignore heartbeat pings
        if (data.type === 'ping') return

        setLatest(data)

        if (TERMINAL_STATUSES.has(data.status)) {
          isTerminalRef.current = true
          setIsTerminal(true)
          ws.close(1000, 'Job terminal')
          if (data.status === 'COMPLETED') onComplete?.(data)
          if (data.status === 'FAILED') onFailed?.(data)
        }
      } catch {
        // non-JSON frame — ignore
      }
    }

    ws.onclose = (event) => {
      setIsConnected(false)
      wsRef.current = null

      if (isTerminalRef.current || !enabled) return

      // Reconnect with backoff
      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = RECONNECT_DELAY_MS * Math.pow(1.5, reconnectAttempts.current)
        reconnectAttempts.current += 1
        reconnectTimer.current = setTimeout(connect, delay)
      } else {
        setError('Lost connection to server. Please refresh to continue.')
      }
    }

    ws.onerror = () => {
      setError('WebSocket connection error')
    }
  }, [jobId, token, enabled, onComplete, onFailed])

  useEffect(() => {
    if (!token || !enabled) return
    connect()

    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close(1000, 'Component unmounted')
      }
    }
  }, [connect, token, enabled])

  return { latest, isConnected, isTerminal, error }
}
