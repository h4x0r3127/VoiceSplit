'use client'

import { useEffect, useRef, useState, useCallback, type RefObject } from 'react'

interface AudioPlayerState {
  isPlaying: boolean
  currentTime: number
  duration: number
  isLoading: boolean
  isReady: boolean
}

interface AudioPlayerControls {
  play: () => void
  pause: () => void
  toggle: () => void
  seek: (time: number) => void
  skip: (seconds: number) => void
  setVolume: (volume: number) => void
  destroy: () => void
}

interface UseAudioPlayerOptions {
  color?: string
  height?: number
  barWidth?: number
  barGap?: number
}

export function useAudioPlayer(
  containerRef: RefObject<HTMLElement | null>,
  url: string,
  options: UseAudioPlayerOptions = {},
): AudioPlayerState & AudioPlayerControls {
  const { color = '#06D6CF', height = 80, barWidth = 3, barGap = 1 } = options

  const wavesurferRef = useRef<import('wavesurfer.js').default | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (!containerRef.current || !url) return

    let cancelled = false

    ;(async () => {
      const WaveSurfer = (await import('wavesurfer.js')).default
      if (cancelled || !containerRef.current) return

      const ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: `${color}66`,
        progressColor: color,
        height,
        barWidth,
        barGap,
        cursorColor: 'rgba(255,255,255,0.5)',
        normalize: true,
        interact: true,
      })

      ws.on('ready', () => {
        if (cancelled) return
        setDuration(ws.getDuration())
        setIsLoading(false)
        setIsReady(true)
      })

      ws.on('timeupdate', (time) => {
        if (!cancelled) setCurrentTime(time)
      })

      ws.on('play', () => { if (!cancelled) setIsPlaying(true) })
      ws.on('pause', () => { if (!cancelled) setIsPlaying(false) })
      ws.on('finish', () => { if (!cancelled) setIsPlaying(false) })

      ws.load(url)
      wavesurferRef.current = ws
    })()

    return () => {
      cancelled = true
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy()
        wavesurferRef.current = null
      }
      setIsPlaying(false)
      setCurrentTime(0)
      setDuration(0)
      setIsLoading(true)
      setIsReady(false)
    }
  }, [url, containerRef, color, height, barWidth, barGap])

  const play = useCallback(() => wavesurferRef.current?.play(), [])
  const pause = useCallback(() => wavesurferRef.current?.pause(), [])
  const toggle = useCallback(() => wavesurferRef.current?.playPause(), [])
  const seek = useCallback((time: number) => {
    if (wavesurferRef.current && duration > 0) {
      wavesurferRef.current.seekTo(time / duration)
    }
  }, [duration])
  const skip = useCallback((seconds: number) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.skip(seconds)
    }
  }, [])
  const setVolume = useCallback((vol: number) => {
    wavesurferRef.current?.setVolume(vol)
  }, [])
  const destroy = useCallback(() => {
    wavesurferRef.current?.destroy()
    wavesurferRef.current = null
  }, [])

  return { isPlaying, currentTime, duration, isLoading, isReady, play, pause, toggle, seek, skip, setVolume, destroy }
}
