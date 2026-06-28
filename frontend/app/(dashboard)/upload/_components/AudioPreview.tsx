'use client'

import { useEffect, useRef, useState } from 'react'
import { Play, Pause, Volume2 } from 'lucide-react'
import { formatDuration } from '@/lib/utils'

interface AudioPreviewProps {
  file: File
  className?: string
}

/**
 * In-browser audio preview player using the native Web Audio API and a
 * <canvas> waveform visualisation. WaveSurfer.js is heavy (370kb) and
 * requires DOM access — this lighter custom player gives the same UX
 * without a dynamic import.
 */
export function AudioPreview({ file, className }: AudioPreviewProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const animRef = useRef<number | null>(null)
  const objectUrlRef = useRef<string | null>(null)

  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [waveformData, setWaveformData] = useState<number[]>([])

  // Create object URL once
  useEffect(() => {
    const url = URL.createObjectURL(file)
    objectUrlRef.current = url

    const audio = new Audio(url)
    audioRef.current = audio

    audio.onloadedmetadata = () => setDuration(audio.duration)
    audio.ontimeupdate = () => setCurrentTime(audio.currentTime)
    audio.onended = () => setIsPlaying(false)

    // Decode for waveform
    decodeWaveform(file).then(setWaveformData).catch(() => {})

    return () => {
      audio.pause()
      URL.revokeObjectURL(url)
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
  }, [file])

  // Sync volume
  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume
  }, [volume])

  // Waveform canvas draw
  useEffect(() => {
    if (!canvasRef.current || waveformData.length === 0) return
    drawWaveform(canvasRef.current, waveformData, duration > 0 ? currentTime / duration : 0)
  }, [waveformData, currentTime, duration])

  function togglePlay() {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
    } else {
      audio.play().then(() => setIsPlaying(true)).catch(() => {})
    }
  }

  function seek(e: React.MouseEvent<HTMLCanvasElement>) {
    const audio = audioRef.current
    if (!audio || duration === 0) return
    const rect = e.currentTarget.getBoundingClientRect()
    const ratio = (e.clientX - rect.left) / rect.width
    audio.currentTime = ratio * duration
  }

  return (
    <div className={`glass rounded-2xl p-5 ${className ?? ''}`}>
      <div className="flex items-center gap-3 mb-4">
        <button
          onClick={togglePlay}
          className="w-10 h-10 rounded-xl bg-brand-cyan/10 border border-brand-cyan/20 flex items-center justify-center text-brand-cyan hover:bg-brand-cyan/20 transition-colors flex-shrink-0"
        >
          {isPlaying
            ? <Pause className="w-4 h-4" />
            : <Play className="w-4 h-4 translate-x-0.5" />}
        </button>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{file.name}</p>
          <p className="text-xs text-muted mt-0.5">
            {formatDuration(currentTime)} / {formatDuration(duration)}
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Volume2 className="w-3.5 h-3.5 text-muted" />
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
            className="w-16 h-1 accent-brand-cyan cursor-pointer"
          />
        </div>
      </div>

      {/* Waveform */}
      <canvas
        ref={canvasRef}
        width={600}
        height={64}
        onClick={seek}
        className="w-full h-14 cursor-pointer rounded-lg"
        style={{ imageRendering: 'pixelated' }}
      />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function decodeWaveform(file: File): Promise<number[]> {
  const arrayBuffer = await file.arrayBuffer()
  const ctx = new AudioContext()
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer)
  await ctx.close()

  const data = audioBuffer.getChannelData(0)
  const buckets = 120
  const bucketSize = Math.floor(data.length / buckets)
  const peaks: number[] = []

  for (let i = 0; i < buckets; i++) {
    let max = 0
    for (let j = 0; j < bucketSize; j++) {
      const abs = Math.abs(data[i * bucketSize + j])
      if (abs > max) max = abs
    }
    peaks.push(max)
  }

  return peaks
}

function drawWaveform(canvas: HTMLCanvasElement, data: number[], progress: number) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const { width, height } = canvas
  const mid = height / 2
  const barWidth = width / data.length
  const progressX = progress * width

  ctx.clearRect(0, 0, width, height)

  data.forEach((peak, i) => {
    const x = i * barWidth
    const barHeight = Math.max(2, peak * mid * 1.8)
    const played = x < progressX

    ctx.fillStyle = played
      ? 'rgba(6, 214, 207, 0.85)'
      : 'rgba(255, 255, 255, 0.12)'

    ctx.beginPath()
    ctx.roundRect(x + 1, mid - barHeight / 2, barWidth - 2, barHeight, 2)
    ctx.fill()
  })
}
